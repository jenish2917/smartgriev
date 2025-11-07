# Video Functionality Removal Plan

## Overview
Removing all video upload and processing functionality from SmartGriev project.

## Frontend Files to Remove/Update

### Files to DELETE completely:
1. `frontend/src/components/MultimodalVideoAnalysis.tsx` - Entire video analysis component
2. `frontend/src/components/MultimodalVideoAnalysis.css` - Video component styles

### Files to UPDATE (remove video references):

#### 1. `frontend/src/components/MultimodalComplaintSubmit.tsx`
- Remove video from FormData interface
- Remove video from PreviewData interface
- Remove video processing status
- Remove video file input handling
- Remove video upload UI section
- Remove video preview section

#### 2. `frontend/src/types/ComplaintCategories.ts`
- Remove video media type from array

#### 3. `frontend/src/pages/Home.tsx`
- Update text: "a photo or video" → "a photo"

#### 4. `frontend/src/pages/Dashboard.tsx`
- Update text: "video, image, or audio" → "image or audio"

## Backend Files to Remove/Update

### Files to UPDATE:

#### 1. `backend/complaints/models.py`
- Remove `video_file` field
- Remove `video_analysis` field
- Update `audio_transcription` help text (remove "video")
- Update `detected_objects` help text (remove "video")

#### 2. `backend/complaints/multimodal_views.py`
- Remove video file handling in create endpoint
- Remove video processing in upload endpoint
- Update documentation strings

#### 3. `backend/machine_learning/video_processor.py`
- Mark as deprecated or delete entirely

## Database Migration Required

Create migration to remove video fields:
```python
# New migration: complaints/migrations/0006_remove_video_fields.py
operations = [
    migrations.RemoveField(
        model_name='complaint',
        name='video_file',
    ),
    migrations.RemoveField(
        model_name='complaint',
        name='video_analysis',
    ),
]
```

## Testing Checklist

After removal:
- [ ] Registration and login work
- [ ] Complaint filing (text only) works
- [ ] Complaint filing with image works
- [ ] Complaint filing with audio works
- [ ] No video-related errors in console
- [ ] All pages load without errors
- [ ] Chatbot functionality intact
- [ ] Dashboard displays correctly

## Implementation Order

1. Frontend cleanup first (safer, no data loss)
2. Backend model updates
3. Create and run database migration
4. Test all functionality
5. Cleanup unused imports
6. Update documentation

## Estimated Impact

- **Frontend**: 5 files to modify, 2 files to delete
- **Backend**: 3 files to modify, 1 file to deprecate
- **Database**: 1 migration to create
- **Risk Level**: Medium (affects data model)
- **Rollback**: Can be reversed via migration rollback

