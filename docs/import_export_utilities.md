# Import/Export Utilities - Part 1: Overview & Data Formats

## Overview
This document provides comprehensive utilities for importing data from existing bridge software (Pianola, Bridgewebs, ACBLscore) and exporting data to standard bridge formats for integration with other systems.

## Data Format Specifications

### 1. Pianola Data Formats

#### Pianola Member Export Format
```typescript
interface PianolaMember {
  MemberID: number;
  MemberNumber: string;
  FirstName: string;
  LastName: string;
  Email: string;
  Mobile: string;
  HomePhone: string;
  Address: string;
  JoinDate: string;
  Status: 'Active' | 'Inactive';
  MemberType: 'Full' | 'Social' | 'Student' | 'Life';
  Notes: string;
}

// CSV format example
const pianolaCSV = `
MemberID,MemberNumber,FirstName,LastName,Email,Mobile,HomePhone,Address,JoinDate,Status,MemberType,Notes
1,123456,John,Smith,john.smith@email.com,+65 9123 4567,+65 6123 4567,"123 Main St, Singapore 123456",2020-01-15,Active,Full,
2,123457,Jane,Doe,jane.doe@email.com,+65 9234 5678,+65 6234 5678,"456 Oak Ave, Singapore 234567",2020-02-20,Active,Full,
`;
```

#### Pianola Results Export Format
```typescript
interface PianolaResult {
  EventID: number;
  EventName: string;
  Date: string;
  PlayerID: number;
  PlayerName: string;
  PartnerID: number;
  PartnerName: string;
  PairNumber: number;
  Score: number;
  Percentage: number;
  Position: number;
  Masterpoints: number;
  Tables: number;
}

// XML format example
const pianolaXML = `
<?xml version="1.0" encoding="UTF-8"?>
<PianolaResults>
  <Event>
    <EventID>123</EventID>
    <EventName>Club Championship</EventName>
    <Date>2025-07-19</Date>
    <Tables>12</Tables>
    <Results>
      <Result>
        <PlayerID>456</PlayerID>
        <PlayerName>John Smith</PlayerName>
        <PartnerID>789</PartnerID>
        <PartnerName>Jane Doe</PartnerName>
        <PairNumber>5</PairNumber>
        <Score>65.5</Score>
        <Percentage>65.5</Percentage>
        <Position>8</Position>
        <Masterpoints>1.25</Masterpoints>
      </Result>
    </Results>
  </Event>
</PianolaResults>
`;
```

### 2. Bridgewebs Data Formats

#### Bridgewebs Member Export
```typescript
interface BridgewebsMember {
  PlayerID: string;
  PlayerName: string;
  Email: string;
  Phone: string;
  Address: string;
  NGSGrade: string;
  MembershipType: string;
  LastPlayed: string;
  TotalPoints: number;
}

// Text format example (fixed width)
const bridgewebsData = `
PlayerID   PlayerName              Email                    Phone           Address                    NGSGrade  MembershipType  LastPlayed  TotalPoints
12345      Smith, John             john.smith@email.com     +65 9123 4567   123 Main St, Singapore     7 Jack    Full           2025-07-15  45.75
12346      Doe, Jane               jane.doe@email.com       +65 9234 5678   456 Oak Ave, Singapore     6 Queen   Full           2025-07-12  52.25
`;
```

#### Bridgewebs Results Export
```typescript
interface BridgewebsResult {
  EventCode: string;
  EventName: string;
  Date: string;
  PlayerNumber: string;
  PlayerName: string;
  PartnerNumber: string;
  PartnerName: string;
  PairNumber: string;
  Score: string;
  Percentage: string;
  Position: string;
  Awards: string;
}

// CSV format with quoted fields
const bridgewebsCSV = `
"EventCode","EventName","Date","PlayerNumber","PlayerName","PartnerNumber","PartnerName","PairNumber","Score","Percentage","Position","Awards"
"CC2025","Club Championship","19/07/2025","12345","Smith, John","12346","Doe, Jane","5","130.5","65.25","8","1.25"
`;
```

### 3. ACBLscore Data Formats

#### ACBLscore Game File Format
```typescript
interface ACBLGame {
  GameNumber: string;
  Date: string;
  EventName: string;
  Movement: string;
  Pairs: number;
  Boards: number;
  Results: ACBLResult[];
}

interface ACBLResult {
  PairNumber: number;
  Direction: 'NS' | 'EW';
  PlayerNumber1: number;
  PlayerName1: string;
  PlayerNumber2: number;
  PlayerName2: string;
  Score: number;
  Percentage: number;
  Position: number;
  Masterpoints: number;
  OverallRank: number;
}

// ACBL game file format (exported text format)
const acblExport = `
ACBL GAME REPORT
================
Game: 123456    Date: 07/19/2025    Event: Club Championship
Movement: Mitchell    Pairs: 24    Boards: 24

Pair Dir Player1         Player2         Score   Pct   Pos  MPs  Rank
---- --- ---------------- --------------- ------- ----- ---- ---- ----
   1  NS Smith, John      Doe, Jane       130.50  65.25    8 1.25   8
   2  EW Brown, Bob       White, Alice    142.75  71.38    3 2.50   3
`;
```

### 4. Standard Bridge Formats

#### PBN (Portable Bridge Notation) Format
```typescript
interface PBNHand {
  boardNumber: number;
  dealer: 'N' | 'S' | 'E' | 'W';
  vulnerability: 'None' | 'NS' | 'EW' | 'All';
  deal: string; // e.g., "N:AKQ.J98.T32.654 T98.AKQ.J98.T32 654.T32.AKQ.J98 J32.654.654.AKQ"
}

// PBN file example
const pbnExample = `
% PBN 2.1
% Export from Bridge Platform
[Event "Club Championship"]
[Date "2025.07.19"]
[Board ""]

[Board "1"]
[Dealer "N"]
[Vulnerable "None"]
[Deal "N:AKQ.J98.T32.654 T98.AKQ.J98.T32 654.T32.AKQ.J98 J32.654.654.AKQ"]

[Board "2"]
[Dealer "E"]
[Vulnerable "NS"]
[Deal "E:J32.654.654.AKQ AKQ.J98.T32.654 T98.AKQ.J98.T32 654.T32.AKQ.J98"]
`;
```

#### XML Bridge Format
```typescript
interface BridgeEventXML {
  event: {
    id: number;
    name: string;
    date: string;
    organization: string;
    type: string;
  };
  results: {
    pairNumber: number;
    player1: string;
    player2: string;
    score: number;
    percentage: number;
    position: number;
    masterpoints: number;
  }[];
}

// XML format example
const bridgeEventXML = `
<?xml version="1.0" encoding="UTF-8"?>
<BridgeEvent>
  <Event>
    <ID>123</ID>
    <Name>Club Championship</Name>
    <Date>2025-07-19</Date>
    <Organization>Singapore Contract Bridge Association</Organization>
    <Type>pairs</Type>
  </Event>
  <Results>
    <Result>
      <PairNumber>1</PairNumber>
      <Player1>John Smith</Player1>
      <Player2>Jane Doe</Player2>
      <Score>130.5</Score>
      <Percentage>65.25</Percentage>
      <Position>8</Position>
      <Masterpoints>1.25</Masterpoints>
    </Result>
  </Results>
</BridgeEvent>
`;
```

## Common Field Mappings

### Member Data Mapping
| Source System | Source Field | Target Field | Notes |
|---------------|--------------|--------------|-------|
| Pianola | MemberID | legacy_pianola_id | Store for reference |
| Pianola | MemberNumber | number | Convert to integer |
| Pianola | FirstName | firstname | Clean and title case |
| Pianola | LastName | lastname | Clean and title case |
| Pianola | Email | email | Lowercase and validate |
| Pianola | Mobile | mobile | Clean format |
| Pianola | HomePhone | homecontact | Clean format |
| Pianola | Address | address | Trim whitespace |
| Pianola | JoinDate | joindate | Parse date format |
| Pianola | Status | status | Map Active/Inactive |
| Bridgewebs | PlayerID | legacy_bridgewebs_id | Store for reference |
| Bridgewebs | PlayerName | firstname, lastname | Parse "Last, First" format |
| ACBLscore | PlayerName1/2 | firstname, lastname | Parse "Last, First" format |

### Results Data Mapping
| Source System | Source Field | Target Field | Notes |
|---------------|--------------|--------------|-------|
| Pianola | EventID | legacy_event_id | Store for reference |
| Pianola | EventName | event.name | Create event if not exists |
| Pianola | Date | event.start_date | Parse date format |
| Pianola | PlayerID | player_id | Lookup by legacy_id |
| Pianola | PartnerID | partner_id | Lookup by legacy_id |
| Pianola | PairNumber | pair_number | Direct mapping |
| Pianola | Score | score | Direct mapping |
| Pianola | Percentage | percentage | Direct mapping |
| Pianola | Position | position | Direct mapping |
| Pianola | Masterpoints | masterpoints_awarded | Direct mapping |
| Bridgewebs | EventCode | event.code | Create event if not exists |
| Bridgewebs | PlayerNumber | player_id | Lookup by number |
| ACBLscore | PairNumber | pair_number | Direct mapping |

## Data Validation Rules

### Member Validation
```typescript
interface MemberValidation {
  number: {
    required: true;
    type: 'integer';
    unique: true;
    min: 1;
    max: 999999;
  };
  firstname: {
    required: true;
    type: 'string';
    minLength: 1;
    maxLength: 100;
    pattern: /^[a-zA-Z\s\-'\.]+$/;
  };
  lastname: {
    required: true;
    type: 'string';
    minLength: 1;
    maxLength: 100;
    pattern: /^[a-zA-Z\s\-'\.]+$/;
  };
  email: {
    required: true;
    type: 'email';
    unique: true;
    maxLength: 255;
  };
  mobile: {
    required: false;
    type: 'string';
    pattern: /^[\+]?[0-9\s\-\(\)]+$/;
  };
  joindate: {
    required: true;
    type: 'date';
    max: 'today';
  };
}
```

### Results Validation
```typescript
interface ResultsValidation {
  score: {
    required: true;
    type: 'number';
    min: 0;
    max: 100; // Percentage-based scoring
  };
  percentage: {
    required: true;
    type: 'number';
    min: 0;
    max: 100;
  };
  position: {
    required: true;
    type: 'integer';
    min: 1;
  };
  pair_number: {
    required: true;
    type: 'integer';
    min: 1;
  };
  masterpoints_awarded: {
    required: false;
    type: 'number';
    min: 0;
    max: 50; // Reasonable upper limit
  };
}
```

## Error Handling Standards

### Import Error Types
```typescript
enum ImportErrorType {
  VALIDATION_ERROR = 'validation_error',
  DUPLICATE_RECORD = 'duplicate_record',
  MISSING_REFERENCE = 'missing_reference',
  DATA_FORMAT_ERROR = 'data_format_error',
  CONSTRAINT_VIOLATION = 'constraint_violation',
  SYSTEM_ERROR = 'system_error'
}

interface ImportError {
  type: ImportErrorType;
  row?: number;
  field?: string;
  value?: string;
  message: string;
  severity: 'error' | 'warning';
  canContinue: boolean;
}
```

### Error Recovery Strategies
```typescript
interface ErrorRecovery {
  validation_error: {
    strategy: 'skip_row' | 'use_default' | 'manual_correction';
    autoCorrect: boolean;
    logLevel: 'warning';
  };
  duplicate_record: {
    strategy: 'skip' | 'update' | 'create_new';
    autoCorrect: true;
    logLevel: 'info';
  };
  missing_reference: {
    strategy: 'create_placeholder' | 'skip_row' | 'manual_intervention';
    autoCorrect: false;
    logLevel: 'error';
  };
}
```

This first part establishes the foundation for all import/export operations. The next parts will contain the actual implementation utilities for each system.