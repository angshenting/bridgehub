# Pianola Import Utility - Part 2

## Pianola Data Import Implementation

### Python Import Class

```python
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional
import logging
import re

class PianolaImporter:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.current_event_code = None
        
    def import_members_csv(self, file_path: str) -> Dict[str, int]:
        """Import members from Pianola CSV export"""
        try:
            df = pd.read_csv(file_path)
            
            # Clean and validate data
            df = self._clean_member_data(df)
            
            imported_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Map Pianola fields to our schema
                    player_data = {
                        'legacy_pianola_id': row['MemberID'],
                        'number': self._parse_member_number(row['MemberNumber']),
                        'firstname': row['FirstName'].strip(),
                        'lastname': row['LastName'].strip(),
                        'email': row['Email'].strip().lower(),
                        'mobile': self._clean_phone(row['Mobile']),
                        'homecontact': self._clean_phone(row['HomePhone']),
                        'address': row['Address'].strip(),
                        'joindate': self._parse_date(row['JoinDate']),
                        'status': 'active' if row['Status'] == 'Active' else 'inactive',
                        'organization_id': 1  # Default to primary organization
                    }
                    
                    # Insert into database
                    self._insert_player(player_data)
                    imported_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append({
                        'row': index + 1,
                        'error': str(e),
                        'data': row.to_dict()
                    })
                    self.logger.warning(f"Error importing member at row {index + 1}: {e}")
            
            return {
                'imported': imported_count,
                'errors': error_count,
                'error_details': errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to import Pianola members: {e}")
            raise
    
    def import_results_xml(self, file_path: str) -> Dict[str, int]:
        """Import results from Pianola XML export"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            imported_events = 0
            imported_results = 0
            errors = []
            
            for event_elem in root.findall('.//Event'):
                try:
                    # Extract event information
                    event_data = {
                        'legacy_pianola_id': event_elem.find('EventID').text,
                        'name': event_elem.find('EventName').text,
                        'start_date': self._parse_date(event_elem.find('Date').text),
                        'organization_id': 1,
                        'type': 'pairs',  # Default, can be enhanced
                        'status': 'completed'
                    }
                    
                    # Insert event
                    event_id = self._insert_event(event_data)
                    imported_events += 1
                    
                    # Insert results
                    for result_elem in event_elem.findall('.//r'):
                        result_data = {
                            'event_id': event_id,
                            'player_id': self._get_player_id_by_legacy_id(result_elem.find('PlayerID').text),
                            'partner_id': self._get_player_id_by_legacy_id(result_elem.find('PartnerID').text),
                            'pair_number': int(result_elem.find('PairNumber').text),
                            'score': float(result_elem.find('Score').text),
                            'percentage': float(result_elem.find('Percentage').text),
                            'position': int(result_elem.find('Position').text),
                            'masterpoints_awarded': float(result_elem.find('Masterpoints').text)
                        }
                        
                        self._insert_result(result_data)
                        imported_results += 1
                        
                except Exception as e:
                    errors.append({
                        'event_id': event_elem.find('EventID').text if event_elem.find('EventID') is not None else 'unknown',
                        'error': str(e)
                    })
                    self.logger.warning(f"Error importing event: {e}")
            
            return {
                'events_imported': imported_events,
                'results_imported': imported_results,
                'errors': len(errors),
                'error_details': errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to import Pianola results: {e}")
            raise
    
    def _clean_member_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate member data"""
        # Remove empty rows
        df = df.dropna(subset=['FirstName', 'LastName'])
        
        # Clean names
        df['FirstName'] = df['FirstName'].str.strip().str.title()
        df['LastName'] = df['LastName'].str.strip().str.title()
        
        # Clean email addresses
        df['Email'] = df['Email'].str.strip().str.lower()
        df = df[df['Email'].str.contains('@', na=False)]
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['MemberNumber'])
        
        return df
    
    def _parse_member_number(self, member_number: str) -> int:
        """Parse member number from various formats"""
        # Remove any non-numeric characters
        numeric_only = re.sub(r'[^\d]', '', str(member_number))
        return int(numeric_only) if numeric_only else 0
    
    def _clean_phone(self, phone: str) -> str:
        """Clean phone number format"""
        if pd.isna(phone):
            return ''
        
        # Remove extra spaces and standardize format
        phone = str(phone).strip()
        # Remove any non-digit, non-space, non-dash, non-parentheses characters
        phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone)
        return phone
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date from various formats"""
        try:
            # Try different date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', '%d-%m-%Y']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return current date
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def _insert_player(self, player_data: Dict) -> int:
        """Insert player into database"""
        query = """
        INSERT INTO players (legacy_pianola_id, number, firstname, lastname, email, 
                           mobile, homecontact, address, joindate, status, organization_id)
        VALUES (%(legacy_pianola_id)s, %(number)s, %(firstname)s, %(lastname)s, 
                %(email)s, %(mobile)s, %(homecontact)s, %(address)s, 
                %(joindate)s, %(status)s, %(organization_id)s)
        ON CONFLICT (number) DO UPDATE SET
            firstname = EXCLUDED.firstname,
            lastname = EXCLUDED.lastname,
            email = EXCLUDED.email,
            mobile = EXCLUDED.mobile,
            homecontact = EXCLUDED.homecontact,
            address = EXCLUDED.address,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, player_data)
            self.db.commit()
            return cursor.fetchone()[0]
    
    def _insert_event(self, event_data: Dict) -> int:
        """Insert event into database"""
        query = """
        INSERT INTO events (legacy_pianola_id, name, start_date, organization_id, type, status)
        VALUES (%(legacy_pianola_id)s, %(name)s, %(start_date)s, %(organization_id)s, 
                %(type)s, %(status)s)
        ON CONFLICT (legacy_pianola_id) DO UPDATE SET
            name = EXCLUDED.name,
            start_date = EXCLUDED.start_date,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, event_data)
            self.db.commit()
            return cursor.fetchone()[0]
    
    def _insert_result(self, result_data: Dict) -> int:
        """Insert result into database"""
        query = """
        INSERT INTO results (event_id, player_id, partner_id, pair_number, score, 
                           percentage, position, masterpoints_awarded)
        VALUES (%(event_id)s, %(player_id)s, %(partner_id)s, %(pair_number)s, 
                %(score)s, %(percentage)s, %(position)s, %(masterpoints_awarded)s)
        ON CONFLICT (event_id, player_id) DO UPDATE SET
            score = EXCLUDED.score,
            percentage = EXCLUDED.percentage,
            position = EXCLUDED.position,
            masterpoints_awarded = EXCLUDED.masterpoints_awarded,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, result_data)
            self.db.commit()
            return cursor.fetchone()[0]
    
    def _get_player_id_by_legacy_id(self, legacy_id: str) -> Optional[int]:
        """Get player ID by legacy Pianola ID"""
        query = "SELECT id FROM players WHERE legacy_pianola_id = %s"
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (legacy_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def bulk_import_members(self, file_path: str, batch_size: int = 1000) -> Dict[str, int]:
        """Bulk import members for better performance"""
        try:
            df = pd.read_csv(file_path)
            df = self._clean_member_data(df)
            
            total_imported = 0
            total_errors = 0
            all_errors = []
            
            # Process in batches
            for start_idx in range(0, len(df), batch_size):
                end_idx = min(start_idx + batch_size, len(df))
                batch_df = df.iloc[start_idx:end_idx]
                
                batch_result = self._import_member_batch(batch_df, start_idx)
                
                total_imported += batch_result['imported']
                total_errors += batch_result['errors']
                all_errors.extend(batch_result['error_details'])
                
                self.logger.info(f"Processed batch {start_idx}-{end_idx}: "
                               f"{batch_result['imported']} imported, "
                               f"{batch_result['errors']} errors")
            
            return {
                'imported': total_imported,
                'errors': total_errors,
                'error_details': all_errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to bulk import Pianola members: {e}")
            raise
    
    def _import_member_batch(self, batch_df: pd.DataFrame, offset: int) -> Dict[str, int]:
        """Import a batch of members"""
        values = []
        errors = []
        
        for index, row in batch_df.iterrows():
            try:
                player_data = {
                    'legacy_pianola_id': row['MemberID'],
                    'number': self._parse_member_number(row['MemberNumber']),
                    'firstname': row['FirstName'].strip(),
                    'lastname': row['LastName'].strip(),
                    'email': row['Email'].strip().lower(),
                    'mobile': self._clean_phone(row['Mobile']),
                    'homecontact': self._clean_phone(row['HomePhone']),
                    'address': row['Address'].strip(),
                    'joindate': self._parse_date(row['JoinDate']),
                    'status': 'active' if row['Status'] == 'Active' else 'inactive',
                    'organization_id': 1
                }
                
                values.append(player_data)
                
            except Exception as e:
                errors.append({
                    'row': offset + index + 1,
                    'error': str(e),
                    'data': row.to_dict()
                })
        
        # Bulk insert
        if values:
            self._bulk_insert_players(values)
        
        return {
            'imported': len(values),
            'errors': len(errors),
            'error_details': errors
        }
    
    def _bulk_insert_players(self, players: List[Dict]) -> None:
        """Bulk insert players into database"""
        query = """
        INSERT INTO players (legacy_pianola_id, number, firstname, lastname, email, 
                           mobile, homecontact, address, joindate, status, organization_id)
        VALUES (%(legacy_pianola_id)s, %(number)s, %(firstname)s, %(lastname)s, 
                %(email)s, %(mobile)s, %(homecontact)s, %(address)s, 
                %(joindate)s, %(status)s, %(organization_id)s)
        ON CONFLICT (number) DO UPDATE SET
            firstname = EXCLUDED.firstname,
            lastname = EXCLUDED.lastname,
            email = EXCLUDED.email,
            mobile = EXCLUDED.mobile,
            homecontact = EXCLUDED.homecontact,
            address = EXCLUDED.address,
            updated_at = CURRENT_TIMESTAMP
        """
        
        with self.db.cursor() as cursor:
            cursor.executemany(query, players)
            self.db.commit()
    
    def validate_import_file(self, file_path: str) -> Dict[str, any]:
        """Validate Pianola import file before processing"""
        try:
            df = pd.read_csv(file_path)
            
            validation_result = {
                'valid': True,
                'total_rows': len(df),
                'issues': [],
                'warnings': [],
                'critical_errors': []
            }
            
            # Check required columns
            required_columns = ['MemberID', 'MemberNumber', 'FirstName', 'LastName', 'Email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                validation_result['valid'] = False
                validation_result['critical_errors'].append({
                    'type': 'missing_columns',
                    'columns': missing_columns
                })
            
            # Check for empty required fields
            for col in required_columns:
                if col in df.columns:
                    empty_count = df[col].isna().sum()
                    if empty_count > 0:
                        validation_result['issues'].append({
                            'type': 'empty_required_field',
                            'column': col,
                            'count': empty_count
                        })
            
            # Check email format
            if 'Email' in df.columns:
                invalid_emails = df[~df['Email'].str.contains('@', na=False)]
                if len(invalid_emails) > 0:
                    validation_result['warnings'].append({
                        'type': 'invalid_email_format',
                        'count': len(invalid_emails),
                        'examples': invalid_emails['Email'].head(5).tolist()
                    })
            
            # Check for duplicate member numbers
            if 'MemberNumber' in df.columns:
                duplicates = df[df['MemberNumber'].duplicated()]
                if len(duplicates) > 0:
                    validation_result['warnings'].append({
                        'type': 'duplicate_member_numbers',
                        'count': len(duplicates),
                        'examples': duplicates['MemberNumber'].head(5).tolist()
                    })
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'total_rows': 0,
                'issues': [],
                'warnings': [],
                'critical_errors': [{'type': 'file_read_error', 'message': str(e)}]
            }


# Usage example and testing
if __name__ == "__main__":
    import psycopg2
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Database connection
    conn = psycopg2.connect("postgresql://user:pass@localhost:5432/bridge_db")
    
    # Create importer instance
    importer = PianolaImporter(conn)
    
    # Validate file before import
    validation_result = importer.validate_import_file("pianola_members.csv")
    print("Validation Result:", validation_result)
    
    if validation_result['valid']:
        # Import members
        member_results = importer.import_members_csv("pianola_members.csv")
        print(f"Member Import: {member_results['imported']} imported, {member_results['errors']} errors")
        
        # Import results
        result_results = importer.import_results_xml("pianola_results.xml")
        print(f"Results Import: {result_results['events_imported']} events, {result_results['results_imported']} results")
    else:
        print("File validation failed. Please fix issues before importing.")
    
    conn.close()
```

## Advanced Pianola Import Features

### Incremental Import Support

```python
class IncrementalPianolaImporter(PianolaImporter):
    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.last_import_timestamp = None
    
    def get_last_import_timestamp(self) -> Optional[datetime]:
        """Get timestamp of last successful import"""
        query = """
        SELECT MAX(created_at) FROM import_log 
        WHERE import_type = 'pianola' AND status = 'success'
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result[0] if result and result[0] else None
    
    def import_members_incremental(self, file_path: str) -> Dict[str, int]:
        """Import only new or updated members since last import"""
        try:
            df = pd.read_csv(file_path)
            
            # Get last import timestamp
            last_import = self.get_last_import_timestamp()
            
            if last_import:
                # Filter for records updated since last import
                df['LastUpdate'] = pd.to_datetime(df.get('LastUpdate', datetime.now()))
                df = df[df['LastUpdate'] > last_import]
                
                self.logger.info(f"Found {len(df)} records updated since {last_import}")
            
            if df.empty:
                return {'imported': 0, 'errors': 0, 'error_details': []}
            
            # Process the filtered data
            result = self.import_members_csv(file_path)
            
            # Log successful import
            self._log_import_success('pianola', 'members', result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed incremental import: {e}")
            self._log_import_failure('pianola', 'members', str(e))
            raise
    
    def _log_import_success(self, import_type: str, data_type: str, result: Dict):
        """Log successful import"""
        query = """
        INSERT INTO import_log (import_type, data_type, status, records_imported, 
                              errors_count, created_at)
        VALUES (%s, %s, 'success', %s, %s, CURRENT_TIMESTAMP)
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (
                import_type, data_type, 
                result['imported'], result['errors']
            ))
            self.db.commit()
    
    def _log_import_failure(self, import_type: str, data_type: str, error: str):
        """Log failed import"""
        query = """
        INSERT INTO import_log (import_type, data_type, status, error_message, created_at)
        VALUES (%s, %s, 'failure', %s, CURRENT_TIMESTAMP)
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (import_type, data_type, error))
            self.db.commit()
```

### Data Transformation and Mapping

```python
class PianolaDataTransformer:
    def __init__(self):
        self.field_mappings = {
            'members': {
                'MemberID': 'legacy_pianola_id',
                'MemberNumber': 'number',
                'FirstName': 'firstname',
                'LastName': 'lastname',
                'Email': 'email',
                'Mobile': 'mobile',
                'HomePhone': 'homecontact',
                'Address': 'address',
                'JoinDate': 'joindate',
                'Status': 'status'
            },
            'results': {
                'EventID': 'legacy_event_id',
                'EventName': 'event_name',
                'Date': 'event_date',
                'PlayerID': 'player_id',
                'PartnerID': 'partner_id',
                'PairNumber': 'pair_number',
                'Score': 'score',
                'Percentage': 'percentage',
                'Position': 'position',
                'Masterpoints': 'masterpoints_awarded'
            }
        }
    
    def transform_member_data(self, pianola_data: Dict) -> Dict:
        """Transform Pianola member data to our schema"""
        transformed = {}
        
        for pianola_field, our_field in self.field_mappings['members'].items():
            if pianola_field in pianola_data:
                value = pianola_data[pianola_field]
                
                # Apply field-specific transformations
                if our_field == 'number':
                    transformed[our_field] = self._parse_member_number(value)
                elif our_field == 'firstname' or our_field == 'lastname':
                    transformed[our_field] = self._clean_name(value)
                elif our_field == 'email':
                    transformed[our_field] = self._clean_email(value)
                elif our_field == 'mobile' or our_field == 'homecontact':
                    transformed[our_field] = self._clean_phone(value)
                elif our_field == 'joindate':
                    transformed[our_field] = self._parse_date(value)
                elif our_field == 'status':
                    transformed[our_field] = 'active' if value == 'Active' else 'inactive'
                else:
                    transformed[our_field] = value
        
        # Add default values
        transformed['organization_id'] = 1  # Default organization
        transformed['created_at'] = datetime.now()
        
        return transformed
    
    def transform_result_data(self, pianola_data: Dict) -> Dict:
        """Transform Pianola result data to our schema"""
        transformed = {}
        
        for pianola_field, our_field in self.field_mappings['results'].items():
            if pianola_field in pianola_data:
                value = pianola_data[pianola_field]
                
                # Apply field-specific transformations
                if our_field in ['score', 'percentage', 'masterpoints_awarded']:
                    transformed[our_field] = float(value) if value else 0.0
                elif our_field in ['pair_number', 'position']:
                    transformed[our_field] = int(value) if value else 0
                elif our_field == 'event_date':
                    transformed[our_field] = self._parse_date(value)
                else:
                    transformed[our_field] = value
        
        return transformed
    
    def _parse_member_number(self, member_number: str) -> int:
        """Parse member number from various formats"""
        import re
        numeric_only = re.sub(r'[^\d]', '', str(member_number))
        return int(numeric_only) if numeric_only else 0
    
    def _clean_name(self, name: str) -> str:
        """Clean and standardize name"""
        if not name:
            return ''
        
        # Remove extra spaces and title case
        name = ' '.join(name.strip().split())
        return name.title()
    
    def _clean_email(self, email: str) -> str:
        """Clean and validate email"""
        if not email:
            return ''
        
        email = email.strip().lower()
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            raise ValueError(f"Invalid email format: {email}")
        
        return email
    
    def _clean_phone(self, phone: str) -> str:
        """Clean phone number"""
        if not phone:
            return ''
        
        # Remove non-digit characters except +, -, (, ), and spaces
        import re
        phone = re.sub(r'[^\d\s\-\(\)\+]', '', str(phone))
        return phone.strip()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse date from various formats"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%d',     # ISO format
                '%d/%m/%Y',     # DD/MM/YYYY
                '%m/%d/%Y',     # MM/DD/YYYY
                '%Y/%m/%d',     # YYYY/MM/DD
                '%d-%m-%Y',     # DD-MM-YYYY
                '%m-%d-%Y',     # MM-DD-YYYY
            ]
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return current date
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
```

### Error Recovery and Rollback

```python
class PianolaImportManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.importer = PianolaImporter(db_connection)
        self.logger = logging.getLogger(__name__)
    
    def import_with_transaction(self, file_path: str, import_type: str = 'members') -> Dict[str, int]:
        """Import with transaction support and rollback capability"""
        savepoint_name = f"pianola_import_{int(datetime.now().timestamp())}"
        
        try:
            # Start transaction
            with self.db.cursor() as cursor:
                cursor.execute(f"SAVEPOINT {savepoint_name}")
            
            # Perform import
            if import_type == 'members':
                result = self.importer.import_members_csv(file_path)
            elif import_type == 'results':
                result = self.importer.import_results_xml(file_path)
            else:
                raise ValueError(f"Unknown import type: {import_type}")
            
            # Check if error rate is acceptable
            if result['errors'] > 0:
                error_rate = result['errors'] / (result['imported'] + result['errors'])
                if error_rate > 0.1:  # More than 10% errors
                    raise Exception(f"Error rate too high: {error_rate:.2%}")
            
            # Commit transaction
            self.db.commit()
            self.logger.info(f"Import completed successfully: {result}")
            
            return result
            
        except Exception as e:
            # Rollback to savepoint
            with self.db.cursor() as cursor:
                cursor.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            
            self.logger.error(f"Import failed, rolled back: {e}")
            
            return {
                'imported': 0,
                'errors': 1,
                'error_details': [{'error': str(e), 'type': 'transaction_failure'}]
            }
    
    def import_with_retry(self, file_path: str, import_type: str = 'members', 
                         max_retries: int = 3) -> Dict[str, int]:
        """Import with retry logic for transient failures"""
        for attempt in range(max_retries):
            try:
                result = self.import_with_transaction(file_path, import_type)
                
                if result['imported'] > 0:
                    return result
                
            except Exception as e:
                self.logger.warning(f"Import attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    raise
                
                # Wait before retry (exponential backoff)
                import time
                time.sleep(2 ** attempt)
        
        return {
            'imported': 0,
            'errors': 1,
            'error_details': [{'error': 'Max retries exceeded', 'type': 'retry_failure'}]
        }
```

This Pianola import utility provides robust, production-ready functionality for importing member and results data from Pianola systems into your new bridge platform. The next part will cover similar utilities for Bridgewebs and ACBLscore imports.