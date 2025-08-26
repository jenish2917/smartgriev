import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import complaintSlice from './slices/complaintSlice';
import dashboardSlice from './slices/dashboardSlice';
import chatbotSlice from './slices/chatbotSlice';
import notificationSlice from './slices/notificationSlice';
import uiSlice from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    complaints: complaintSlice,
    dashboard: dashboardSlice,
    chatbot: chatbotSlice,
    notifications: notificationSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
  devTools: import.meta.env.DEV,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
