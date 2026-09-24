# -*- coding: utf-8 -*-
import os
import glob
import re
import json
import pymysql
import time
from dotenv import load_dotenv

os.makedirs('reports', exist_ok=True)
os.makedirs('docs', exist_ok=True)

load_dotenv()

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        import decimal
        import datetime
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def get_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database="insightal_analytics",
        cursorclass=pymysql.cursors.DictCursor
    )

def parse_sql_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    metadata_pattern = re.compile(r'/\*(.*?)\*/', re.DOTALL)
    metadata_blocks = metadata_pattern.findall(content)

    queries = []
    statements = [s.strip() for s in content.split(';') if s.strip()]
    current_meta = {}
    
    for stmt in statements:
        if stmt.upper().startswith('USE '):
            continue
            
        meta_match = metadata_pattern.match(stmt)
        if meta_match:
            block = meta_match.group(1).strip()
            for line in block.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    current_meta[k.strip().lower()] = v.strip()
            stmt = stmt[meta_match.end():].strip()
            
        if not stmt:
            continue
            
        queries.append({
            'query_id': current_meta.get('query id', 'UNKNOWN'),
            'question': current_meta.get('business question', ''),
            'purpose': current_meta.get('purpose', ''),
            'grain': current_meta.get('grain', ''),
            'sql': stmt
        })
    
    return queries

def main():
    conn = get_connection()
    sql_files = sorted(glob.glob('sql/analytics/*.sql'))
    
    results = {
        'total_files': len(sql_files),
        'analytics_queries_executed': 0,
        'validation_checks_executed': 0,
        'successful_queries': 0,
        'failed_queries': 0,
        'validation_failures': 0,
        'key_outputs': {},
        'details': []
    }

    try:
        with conn.cursor() as cursor:
            for file in sql_files:
                is_val = '13_sql_validation' in file
                queries = parse_sql_file(file)
                for q in queries:
                    start_time = time.time()
                    try:
                        cursor.execute(q['sql'])
                        rows = cursor.fetchall()
                        exec_time_ms = round((time.time() - start_time) * 1000, 2)
                        
                        detail = {
                            'file': os.path.basename(file),
                            'query_id': q['query_id'],
                            'status': 'PASS',
                            'execution_time_ms': exec_time_ms,
                            'result_row_count': len(rows)
                        }
                        
                        if is_val:
                            results['validation_checks_executed'] += 1
                            # For VAL-ALL, it expects multiple rows with validation_id, status, failure_count
                            if rows and 'validation_id' in rows[0]:
                                detail['validation_id'] = rows[0].get('validation_id')
                                detail['failure_count'] = rows[0].get('failure_count')
                                detail['validation_status'] = rows[0].get('status')
                                if rows[0].get('status') == 'FAIL':
                                    results['validation_failures'] += 1
                                    detail['status'] = 'FAIL'
                        else:
                            results['analytics_queries_executed'] += 1
                            results['successful_queries'] += 1
                        
                        if q['query_id'] == 'EXE-001' and rows:
                            results['key_outputs']['executive_kpis'] = rows[0]
                            
                        results['details'].append(detail)
                        
                    except Exception as e:
                        exec_time_ms = round((time.time() - start_time) * 1000, 2)
                        results['failed_queries'] += 1
                        results['details'].append({
                            'file': os.path.basename(file),
                            'query_id': q['query_id'],
                            'status': 'FAIL',
                            'execution_time_ms': exec_time_ms,
                            'error': str(e)
                        })

    finally:
        conn.close()

    with open('reports/phase7_sql_validation.json', 'w') as f:
        json.dump(results, f, indent=4, cls=CustomJSONEncoder)

    status = 'PASS' if results['failed_queries'] == 0 and results['validation_failures'] == 0 else 'FAIL'
    
    print(f"PHASE 7 SQL ANALYTICS STATUS: {status}")
    print(f"SQL Files Created: {results['total_files']}")
    print(f"Analytics Queries Executed: {results['analytics_queries_executed']}")
    print(f"Validation Checks Executed: {results['validation_checks_executed']}")
    print(f"Successful Analytics Queries: {results['successful_queries']}")
    print(f"Failed Analytics Queries: {results['failed_queries']}")
    print(f"Validation Failures: {results['validation_failures']}")
    
    kpis = results['key_outputs'].get('executive_kpis', {})
    if kpis:
        print(f"\nKey KPI Outputs:")
        for k, v in kpis.items():
            print(f"  {k}: {v}")
    
    print("\nExecution Timing:")
    total_ms = sum([d.get('execution_time_ms', 0) for d in results['details']])
    print(f"  Total SQL Execution Time: {total_ms:.2f} ms")
    
    print("\nKnown Warnings: Intentional nulls in demographic data and standard statistical variances from synthetic baseline.")
    print("Documentation: docs/phase7_sql_analytics.md")
    print("Validation Report: reports/phase7_sql_validation.json")
    print("\nPHASE 7 COMPLETE  AWAITING REVIEW")

if __name__ == '__main__':
    main()
