import { createSlice } from '@reduxjs/toolkit';

interface ComplaintState {
  complaints: any[];
  loading: boolean;
  error: string | null;
}

const initialState: ComplaintState = {
  complaints: [],
  loading: false,
  error: null,
};

const complaintSlice = createSlice({
  name: 'complaints',
  initialState,
  reducers: {
    setComplaints: (state, action) => {
      state.complaints = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const { setComplaints, setLoading, setError } = complaintSlice.actions;
export default complaintSlice.reducer;
