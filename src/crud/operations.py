import pandas as pd
from sqlalchemy import text
from datetime import datetime
import sys
import os

# Ensure we can import db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.database.load_database import get_db_connection, engine

def ensure_audit_table_exists():
    """Creates the audit table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS audit_log (
        id SERIAL PRIMARY KEY,
        table_name TEXT,
        action TEXT,
        record_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()

def save_changes(original_df: pd.DataFrame, edited_df: pd.DataFrame, table_name: str, pk_col: str = "operation_id", user: str = "Admin"):
    """
    Compares original and edited dataframes, applies changes to DB, and logs to audit.
    original_df and edited_df MUST have the Primary Key as the Index.
    """
    ensure_audit_table_exists()
    
    # Identify changes
    original_ids = set(original_df.index)
    edited_ids = set(edited_df.index)
    
    deleted_ids = original_ids - edited_ids
    added_ids = edited_ids - original_ids
    common_ids = original_ids & edited_ids
    
    updated_ids = []
    for idx in common_ids:
        # Compare rows. Note: we need to handle NaN comparison correctly or types.
        # Simple equals might fail if types changed slightly (int vs float).
        # For simplicity in this brief, we use straightforward comparison.
        row_org = original_df.loc[idx]
        row_new = edited_df.loc[idx]
        
        # We can align them and compare
        if not row_org.equals(row_new):
            updated_ids.append(idx)
            
    # Execute Transactions
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            # DELETE
            if deleted_ids:
                # Need to quote table name in case
                ids_tuple = tuple(deleted_ids)
                if len(deleted_ids) == 1:
                    # tuple( {1} ) -> (1,) which is correct for SQL IN
                    pass
                
                # Using text() with parameter binding for safety
                # But creating a dynamic IN clause is tricky with bind params for list
                # For safety/simplicity loop or use specific postgres Any
                
                # Delete query
                delete_q = text(f'DELETE FROM "{table_name}" WHERE "{pk_col}" = :id')
                for del_id in deleted_ids:
                    conn.execute(delete_q, {"id": del_id})
                    
                # Audit
                conn.execute(text("""
                    INSERT INTO audit_log (table_name, action, record_id)
                    VALUES (:table, 'DELETE', :details)
                """), {"table": table_name, "details": f"Deleted IDs: {deleted_ids}"})

            # INSERT
            if added_ids:
                # Get the new rows
                new_rows = edited_df.loc[list(added_ids)]
                # Append to DB efficiently using pandas
                # But we want to do it safely. to_sql might fail if table exists depending on args.
                # 'append' mode.
                # However, we are inside a transaction manually started? pandas to_sql manages its own connection usually,
                # but we can pass 'conn'.
                
                # Note: to_sql with 'append' keeps the table structure.
                # We need to make sure columns match.
                new_rows.to_sql(table_name, conn, if_exists='append', index=True, schema=None) 
                # index=True because we want the PK (which is the index) to be inserted?
                # The table definition says operation_id is PK. If it's in the index of DF, we verify if to_sql handles index label as column.
                # If index has name 'operation_id', pandas to_sql uses it as column if index=True.
                
                conn.execute(text("""
                    INSERT INTO audit_log (table_name, action, record_id)
                    VALUES (:table, 'INSERT', :details)
                """), {"table": table_name, "details": f"Inserted IDs: {added_ids}"})

            # UPDATE
            if updated_ids:
                update_q_base = f'UPDATE "{table_name}" SET '
                
                for uid in updated_ids:
                    row = edited_df.loc[uid]
                    # Generate SET clause
                    # We only update columns that exist in the DB (assuming DF cols match DB cols)
                    # We skip the PK in SET 
                    
                    params = {"pk": uid}
                    set_parts = []
                    for col in edited_df.columns:
                        set_parts.append(f'"{col}" = :{col}')
                        # Handle basic types
                        val = row[col]
                        # Convert numpy types to python native
                        if hasattr(val, 'item'): 
                            val = val.item()
                        params[col] = val
                    
                    full_q = update_q_base + ", ".join(set_parts) + f' WHERE "{pk_col}" = :pk'
                    
                    conn.execute(text(full_q), params)
                
                conn.execute(text("""
                    INSERT INTO audit_log (table_name, action, record_id)
                    VALUES (:table, 'UPDATE', :details)
                """), {"table": table_name, "details": f"Updated IDs: {updated_ids}"})
                
            transaction.commit()
            return True, f"Success: +{len(added_ids)} rows, -{len(deleted_ids)} rows, ~{len(updated_ids)} rows."
            
        except Exception as e:
            transaction.rollback()
            return False, str(e)
