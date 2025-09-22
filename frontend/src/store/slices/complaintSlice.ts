import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { complaintService, UpdateComplaintData, ComplaintFilters } from '@/services/complaintService';
import type { 
  Complaint, 
  CreateComplaintData, 
  PaginatedResponse
} from '@/types';

// Async thunks
export const fetchComplaints = createAsyncThunk(
  'complaints/fetchComplaints',
  async (filters: ComplaintFilters = {}, { rejectWithValue }) => {
    try {
      return await complaintService.getComplaints(filters);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch complaints');
    }
  }
);

export const fetchComplaint = createAsyncThunk(
  'complaints/fetchComplaint',
  async (id: number, { rejectWithValue }) => {
    try {
      return await complaintService.getComplaint(id);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch complaint');
    }
  }
);

export const createComplaint = createAsyncThunk(
  'complaints/createComplaint',
  async (data: CreateComplaintData, { rejectWithValue }) => {
    try {
      return await complaintService.createComplaint(data);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to create complaint');
    }
  }
);

export const updateComplaint = createAsyncThunk(
  'complaints/updateComplaint',
  async ({ id, data }: { id: number; data: UpdateComplaintData }, { rejectWithValue }) => {
    try {
      return await complaintService.updateComplaint(id, data);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to update complaint');
    }
  }
);

export const deleteComplaint = createAsyncThunk(
  'complaints/deleteComplaint',
  async (id: number, { rejectWithValue }) => {
    try {
      await complaintService.deleteComplaint(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to delete complaint');
    }
  }
);

export const fetchUserComplaints = createAsyncThunk(
  'complaints/fetchUserComplaints',
  async (params: { page?: number; page_size?: number; status?: string } = {}, { rejectWithValue }) => {
    try {
      return await complaintService.getUserComplaints(params);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch user complaints');
    }
  }
);

export const updateComplaintStatus = createAsyncThunk(
  'complaints/updateComplaintStatus',
  async ({ id, status, notes }: { id: number; status: string; notes?: string }, { rejectWithValue }) => {
    try {
      return await complaintService.updateComplaintStatus(id, status, notes);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to update complaint status');
    }
  }
);

export const assignComplaint = createAsyncThunk(
  'complaints/assignComplaint',
  async ({ id, officer_id }: { id: number; officer_id: number }, { rejectWithValue }) => {
    try {
      return await complaintService.assignComplaint(id, officer_id);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to assign complaint');
    }
  }
);

export const fetchComplaintStats = createAsyncThunk(
  'complaints/fetchComplaintStats',
  async (_, { rejectWithValue }) => {
    try {
      return await complaintService.getComplaintStats();
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch complaint stats');
    }
  }
);

export const searchComplaints = createAsyncThunk(
  'complaints/searchComplaints',
  async ({ query, filters }: { query: string; filters?: any }, { rejectWithValue }) => {
    try {
      return await complaintService.searchComplaints(query, filters);
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to search complaints');
    }
  }
);

// State interface
interface ComplaintState {
  // Complaint lists
  complaints: Complaint[];
  userComplaints: Complaint[];
  searchResults: Complaint[];
  
  // Current complaint
  currentComplaint: Complaint | null;
  
  // Pagination
  pagination: {
    count: number;
    next: string | null;
    previous: string | null;
    currentPage: number;
    pageSize: number;
  };
  
  // Statistics
  stats: {
    total: number;
    pending: number;
    resolved: number;
    by_category: Array<{ category: string; count: number }>;
    by_status: Array<{ status: string; count: number }>;
  } | null;
  
  // Loading states
  loading: {
    list: boolean;
    detail: boolean;
    create: boolean;
    update: boolean;
    delete: boolean;
    stats: boolean;
    search: boolean;
  };
  
  // Error states
  error: {
    list: string | null;
    detail: string | null;
    create: string | null;
    update: string | null;
    delete: string | null;
    stats: string | null;
    search: string | null;
  };
  
  // UI state
  filters: ComplaintFilters;
  selectedComplaints: number[];
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

const initialState: ComplaintState = {
  complaints: [],
  userComplaints: [],
  searchResults: [],
  currentComplaint: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
    currentPage: 1,
    pageSize: 10,
  },
  stats: null,
  loading: {
    list: false,
    detail: false,
    create: false,
    update: false,
    delete: false,
    stats: false,
    search: false,
  },
  error: {
    list: null,
    detail: null,
    create: null,
    update: null,
    delete: null,
    stats: null,
    search: null,
  },
  filters: {},
  selectedComplaints: [],
  sortBy: 'created_at',
  sortOrder: 'desc',
};

const complaintSlice = createSlice({
  name: 'complaints',
  initialState,
  reducers: {
    // UI actions
    setFilters: (state, action: PayloadAction<ComplaintFilters>) => {
      state.filters = action.payload;
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setSelectedComplaints: (state, action: PayloadAction<number[]>) => {
      state.selectedComplaints = action.payload;
    },
    toggleComplaintSelection: (state, action: PayloadAction<number>) => {
      const id = action.payload;
      if (state.selectedComplaints.includes(id)) {
        state.selectedComplaints = state.selectedComplaints.filter(cId => cId !== id);
      } else {
        state.selectedComplaints.push(id);
      }
    },
    selectAllComplaints: (state) => {
      state.selectedComplaints = state.complaints.map(c => c.id);
    },
    clearSelection: (state) => {
      state.selectedComplaints = [];
    },
    setSorting: (state, action: PayloadAction<{ sortBy: string; sortOrder: 'asc' | 'desc' }>) => {
      state.sortBy = action.payload.sortBy;
      state.sortOrder = action.payload.sortOrder;
    },
    clearCurrentComplaint: (state) => {
      state.currentComplaint = null;
    },
    clearErrors: (state) => {
      state.error = {
        list: null,
        detail: null,
        create: null,
        update: null,
        delete: null,
        stats: null,
        search: null,
      };
    },
  },
  extraReducers: (builder) => {
    // Fetch complaints
    builder
      .addCase(fetchComplaints.pending, (state) => {
        state.loading.list = true;
        state.error.list = null;
      })
      .addCase(fetchComplaints.fulfilled, (state, action: PayloadAction<PaginatedResponse<Complaint>>) => {
        state.loading.list = false;
        state.complaints = action.payload.results;
        state.pagination = {
          count: action.payload.count,
          next: action.payload.next,
          previous: action.payload.previous,
          currentPage: Math.floor((action.payload.results.length || 0) / state.pagination.pageSize) + 1,
          pageSize: state.pagination.pageSize,
        };
      })
      .addCase(fetchComplaints.rejected, (state, action) => {
        state.loading.list = false;
        state.error.list = action.payload as string;
      });

    // Fetch single complaint
    builder
      .addCase(fetchComplaint.pending, (state) => {
        state.loading.detail = true;
        state.error.detail = null;
      })
      .addCase(fetchComplaint.fulfilled, (state, action: PayloadAction<Complaint>) => {
        state.loading.detail = false;
        state.currentComplaint = action.payload;
      })
      .addCase(fetchComplaint.rejected, (state, action) => {
        state.loading.detail = false;
        state.error.detail = action.payload as string;
      });

    // Create complaint
    builder
      .addCase(createComplaint.pending, (state) => {
        state.loading.create = true;
        state.error.create = null;
      })
      .addCase(createComplaint.fulfilled, (state, action: PayloadAction<Complaint>) => {
        state.loading.create = false;
        state.complaints.unshift(action.payload);
        state.pagination.count += 1;
      })
      .addCase(createComplaint.rejected, (state, action) => {
        state.loading.create = false;
        state.error.create = action.payload as string;
      });

    // Update complaint
    builder
      .addCase(updateComplaint.pending, (state) => {
        state.loading.update = true;
        state.error.update = null;
      })
      .addCase(updateComplaint.fulfilled, (state, action: PayloadAction<Complaint>) => {
        state.loading.update = false;
        const index = state.complaints.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.complaints[index] = action.payload;
        }
        if (state.currentComplaint?.id === action.payload.id) {
          state.currentComplaint = action.payload;
        }
      })
      .addCase(updateComplaint.rejected, (state, action) => {
        state.loading.update = false;
        state.error.update = action.payload as string;
      });

    // Delete complaint
    builder
      .addCase(deleteComplaint.pending, (state) => {
        state.loading.delete = true;
        state.error.delete = null;
      })
      .addCase(deleteComplaint.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading.delete = false;
        state.complaints = state.complaints.filter(c => c.id !== action.payload);
        state.pagination.count -= 1;
        if (state.currentComplaint?.id === action.payload) {
          state.currentComplaint = null;
        }
      })
      .addCase(deleteComplaint.rejected, (state, action) => {
        state.loading.delete = false;
        state.error.delete = action.payload as string;
      });

    // Update complaint status
    builder
      .addCase(updateComplaintStatus.fulfilled, (state, action: PayloadAction<Complaint>) => {
        const index = state.complaints.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.complaints[index] = action.payload;
        }
        if (state.currentComplaint?.id === action.payload.id) {
          state.currentComplaint = action.payload;
        }
      });

    // Assign complaint
    builder
      .addCase(assignComplaint.fulfilled, (state, action: PayloadAction<Complaint>) => {
        const index = state.complaints.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.complaints[index] = action.payload;
        }
        if (state.currentComplaint?.id === action.payload.id) {
          state.currentComplaint = action.payload;
        }
      });

    // Fetch user complaints
    builder
      .addCase(fetchUserComplaints.fulfilled, (state, action: PayloadAction<PaginatedResponse<Complaint>>) => {
        state.userComplaints = action.payload.results;
      });

    // Fetch complaint stats
    builder
      .addCase(fetchComplaintStats.pending, (state) => {
        state.loading.stats = true;
        state.error.stats = null;
      })
      .addCase(fetchComplaintStats.fulfilled, (state, action) => {
        state.loading.stats = false;
        state.stats = action.payload;
      })
      .addCase(fetchComplaintStats.rejected, (state, action) => {
        state.loading.stats = false;
        state.error.stats = action.payload as string;
      });

    // Search complaints
    builder
      .addCase(searchComplaints.pending, (state) => {
        state.loading.search = true;
        state.error.search = null;
      })
      .addCase(searchComplaints.fulfilled, (state, action: PayloadAction<Complaint[]>) => {
        state.loading.search = false;
        state.searchResults = action.payload;
      })
      .addCase(searchComplaints.rejected, (state, action) => {
        state.loading.search = false;
        state.error.search = action.payload as string;
      });
  },
});

export const {
  setFilters,
  clearFilters,
  setSelectedComplaints,
  toggleComplaintSelection,
  selectAllComplaints,
  clearSelection,
  setSorting,
  clearCurrentComplaint,
  clearErrors,
} = complaintSlice.actions;

export default complaintSlice.reducer;
