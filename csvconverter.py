import os
import csv
import json
import subprocess

CSV_FOLDER = 'csvfile' #csv folder name
OUTPUT_FOLDER = 'output' #convert result folder name
DB_NAME = 'sekolah' #database name(mongo)

def csv_to_insert_script(csv_path, output_path, collection_name):
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        documents = []

        for row in reader:
            clean_row = {}
            for k, v in row.items():
                v = v.strip()
                if v.isdigit():
                    clean_row[k] = int(v)
                elif v.lower() in ['null', 'none', '']:
                    clean_row[k] = None
                else:
                    try:  
                        clean_row[k] = int(v)
                    except ValueError:
                        try:
                            clean_row[k] = float(v)
                        except ValueError:
                            clean_row[k] = v
            documents.append(clean_row)

    insert_statement = f'db.{collection_name}.insertMany({json.dumps(documents, indent=2)});'

    #Validating Output Folder
    os. makedirs(OUTPUT_FOLDER, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(insert_statement)
    print(f'✅ File Converted: {csv_path} → {output_path}')

def run_mongosh_script(script_path):
    print(f'🚀 Importing to MongoDB from: {script_path}')
    result = subprocess.run(
        ['mongosh', DB_NAME, script_path],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f'✅ Successfully Imported: {os.path.basename(script_path)}')
    else:
        print(f'❌ Failed to import {os.path.basename(script_path)}:')
        print(result.stderr)

def main():
    if not os.path.isdir(CSV_FOLDER):
        print(f'📁 Folder "{CSV_FOLDER}" not found.')
        return
    
    for filename in os.listdir(CSV_FOLDER):
        if filename.endswith('.csv'):
            collection_name = os.path.splitext(filename)[0].lower()
            csv_path = os.path.join(CSV_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, f'{collection_name}.js')
            
            csv_to_insert_script(csv_path, output_path, collection_name)
            run_mongosh_script(output_path)

if __name__ == '__main__':
    main()
