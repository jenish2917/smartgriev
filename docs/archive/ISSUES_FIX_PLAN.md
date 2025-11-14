# SmartGriev Issues Fix Plan

## Issues Identified from Screenshots

### 1. **Language Switching Not Working Fully** ❌
**Problem**: Language changes sometimes don't apply to all parts
**Root Cause**: i18n language is saved but not all components are re-rendering
**Solution**: 
- i18n.ts already has localStorage integration ✅
- Need to ensure all components use `useTranslation()` hook
- Add language change listener in main.tsx

### 2. **Chatbot Not Understanding Selected Language** ❌
**Problem**: Chatbot shows errors like "Sorry, I encountered an error"
**Root Cause**: 
- Language not being passed correctly to backend
- Backend gemini_service.py has translation but may have issues
**Solution**:
- Fix ChatbotPage.tsx to properly pass `i18n.language` to API
- Update backend to handle language parameter correctly
- Ensure Gemini responds in requested language

### 3. **All Complaints Showing for All Users** ❌
**Problem**: Dashboard shows all complaints instead of user-specific
**Root Cause**: complaints/views.py line 34 filters correctly but frontend may be calling wrong endpoint or not filtering
**Solution**:
- Check complaints API endpoint
- Verify frontend is using authenticated user's complaints only
- Remove any hardcoded example complaints

### 4. **Auto-Escalation Missing** ❌
**Problem**: No automatic escalation for complaints not resolved in 2-3 days
**Solution**:
- Create Django management command
- Add celery task for daily checks
- Update complaint status and notify departments

### 5. **TypeScript/ESLint Errors** ⚠️
**Problems**:
- `Home.tsx`: Missing styled-components import
- `Input.tsx`: Invalid ARIA attribute
- `ChatbotPage.tsx`: Button missing discernible text

## Fix Priority

1. **HIGH**: Fix chatbot language understanding (User can't use chatbot properly)
2. **HIGH**: Fix complaints filtering (Privacy/security issue - users seeing others' complaints)
3. **MEDIUM**: Fix language switching persistence
4. **MEDIUM**: Add auto-escalation
5. **LOW**: Fix TypeScript errors

## Implementation Steps

### Step 1: Fix Chatbot Language (HIGH PRIORITY)
Files to modify:
- `backend/chatbot/gemini_service.py` - Ensure translation works
- `backend/chatbot/views.py` - Pass language correctly
- `frontend-new/src/api/chatbot.ts` - Send language in API call
- `frontend-new/src/pages/chatbot/ChatbotPage.tsx` - Use i18n.language

### Step 2: Fix Complaints Filtering (HIGH PRIORITY)
Files to modify:
- `backend/complaints/views.py` - Verify user filtering
- `frontend-new/src/pages/dashboard/DashboardPage.tsx` - Remove hardcoded complaints
- `frontend-new/src/api/complaints.ts` - Ensure correct endpoint

### Step 3: Auto-Escalation (MEDIUM PRIORITY)
Files to create:
- `backend/complaints/management/commands/escalate_complaints.py`
- `backend/complaints/tasks.py` (if using Celery)

### Step 4: Language Persistence (MEDIUM PRIORITY)
Files to modify:
- `frontend-new/src/main.tsx` - Load saved language on init
- `frontend-new/src/lib/i18n.ts` - Already done ✅

### Step 5: Fix TypeScript Errors (LOW PRIORITY)
Files to modify:
- `frontend-new/src/pages/Home.tsx`
- `frontend-new/src/components/atoms/Input.tsx`
- `frontend-new/src/pages/chatbot/ChatbotPage.tsx`
