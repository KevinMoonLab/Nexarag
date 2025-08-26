# Knowledge Graph Export/Load Feature

This feature allows users to export, save, and switch between different Neo4j knowledge graphs in the Nexarag platform.

## Overview

The Knowledge Graph Management feature provides:

1. **Export Current KG**: Save the current knowledge graph to a dump file
2. **Import/Load KG**: Switch to a previously saved knowledge graph
3. **List Available KGs**: View all saved knowledge graphs with metadata
4. **Delete KGs**: Remove unwanted knowledge graph dumps
5. **Quick Selector**: Dropdown menu to quickly switch between knowledge graphs

## Backend Implementation

### API Endpoints

- `GET /kg/list/` - List all available knowledge graph dumps
- `POST /kg/export/` - Export current knowledge graph
- `POST /kg/import/` - Import/load a knowledge graph
- `DELETE /kg/delete/` - Delete a knowledge graph dump
- `GET /kg/current/` - Get current knowledge graph information

### Docker Changes

Added `kg_dumps` volume to all docker-compose files:
- `docker-compose.cpu.yml`
- `docker-compose.gpu.yml` 
- `docker-compose.macos.yml`

This volume is mounted at `/dumps` in the Neo4j container and shared with API and KG services.

### KnowledgeGraphManager Class

Located in `backend/src/kg/db/kg_manager.py`, this class handles:
- Exporting databases using `neo4j-admin database dump`
- Loading databases using `neo4j-admin database load`
- Managing metadata for saved knowledge graphs
- File operations for dump files

## Frontend Implementation

### New Components

1. **KgManagementComponent** (`frontend/src/app/kg/kg-management.component.ts`)
   - Full knowledge graph management interface
   - Export form with name and description
   - Grid view of available knowledge graphs
   - Load/delete actions for each KG

2. **KgSelectorComponent** (`frontend/src/app/kg/kg-selector.component.ts`)
   - Compact dropdown selector
   - Quick switching between knowledge graphs
   - Positioned at top of main viewport

3. **KnowledgeGraphService** (`frontend/src/app/kg/kg.service.ts`)
   - HTTP service for KG API calls
   - TypeScript interfaces for API responses

### UI Integration

- Added new "Knowledge Graphs" tab to the main menu (database icon)
- Added KG selector dropdown at the top of the main viewport
- Toast notifications for all operations
- Confirmation dialogs for destructive actions

## Usage

### Exporting a Knowledge Graph

1. Open the Knowledge Graphs tab in the menu
2. Enter a name for your export (required)
3. Optionally add a description
4. Click "Export Knowledge Graph"
5. The current Neo4j database will be saved as a dump file

### Switching Knowledge Graphs

**Option 1: Quick Selector**
1. Use the dropdown at the top of the screen
2. Select a knowledge graph from the list
3. The system will automatically load the selected KG

**Option 2: Management Interface**
1. Open the Knowledge Graphs tab
2. Click "Load" button on any knowledge graph card
3. Confirm the action

### Deleting Knowledge Graphs

1. Open the Knowledge Graphs tab
2. Click "Delete" button on the knowledge graph card
3. Confirm the deletion in the popup dialog

## Technical Notes

### Neo4j Commands

The system uses Neo4j 5.x admin commands:
- Export: `neo4j-admin database dump --to-path=/dumps --database=<name> --overwrite-destination=true`
- Import: `neo4j-admin database load --from-path=/dumps --database=<name> --overwrite-destination=true`

### Database Operations

When loading a knowledge graph:
1. Neo4j database is stopped
2. Dump file is loaded
3. Database is restarted

This ensures data consistency but causes a brief service interruption.

### Metadata Storage

Knowledge graph metadata is stored in `kg_metadata.json` within the dumps volume:
```json
{
  "kg_name": {
    "created_at": "ISO datetime",
    "description": "User description",
    "database": "neo4j database name"
  }
}
```

### Volume Persistence

The `kg_dumps` volume persists knowledge graphs across container restarts. However, if you remove the volume, all saved knowledge graphs will be lost.

## Limitations

1. **Single Database**: Currently supports one active database at a time
2. **Service Interruption**: Loading a KG briefly stops the Neo4j service
3. **Storage Space**: Large knowledge graphs require significant storage
4. **No Compression**: Dump files are stored uncompressed

## Future Enhancements

1. **Parallel Databases**: Support multiple concurrent databases
2. **Compression**: Compress dump files to save space
3. **Import/Export Progress**: Show progress bars for large operations
4. **KG Comparison**: Compare differences between knowledge graphs
5. **Scheduled Exports**: Automatic periodic backups
6. **Cloud Storage**: Upload/download KGs to/from cloud storage
