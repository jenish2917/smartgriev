import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark';
  loading: Record<string, boolean>;
  errors: Record<string, string | null>;
  modals: Record<string, boolean>;
  activeTab: string;
  pageTitle: string;
  breadcrumbs: Array<{ title: string; path?: string }>;
}

const initialState: UIState = {
  sidebarCollapsed: false,
  theme: 'light',
  loading: {},
  errors: {},
  modals: {},
  activeTab: 'dashboard',
  pageTitle: 'Dashboard',
  breadcrumbs: [{ title: 'Dashboard' }],
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload;
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    setLoading: (state, action: PayloadAction<{ key: string; loading: boolean }>) => {
      state.loading[action.payload.key] = action.payload.loading;
    },
    setError: (state, action: PayloadAction<{ key: string; error: string | null }>) => {
      state.errors[action.payload.key] = action.payload.error;
    },
    clearError: (state, action: PayloadAction<string>) => {
      delete state.errors[action.payload];
    },
    clearAllErrors: (state) => {
      state.errors = {};
    },
    setModal: (state, action: PayloadAction<{ key: string; open: boolean }>) => {
      state.modals[action.payload.key] = action.payload.open;
    },
    closeAllModals: (state) => {
      state.modals = {};
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload;
    },
    setPageTitle: (state, action: PayloadAction<string>) => {
      state.pageTitle = action.payload;
    },
    setBreadcrumbs: (state, action: PayloadAction<Array<{ title: string; path?: string }>>) => {
      state.breadcrumbs = action.payload;
    },
  },
});

export const {
  toggleSidebar,
  setSidebarCollapsed,
  setTheme,
  setLoading,
  setError,
  clearError,
  clearAllErrors,
  setModal,
  closeAllModals,
  setActiveTab,
  setPageTitle,
  setBreadcrumbs,
} = uiSlice.actions;

export default uiSlice.reducer;
