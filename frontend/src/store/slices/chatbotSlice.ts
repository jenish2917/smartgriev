import { createSlice } from '@reduxjs/toolkit';

interface ChatbotState {
  messages: any[];
  loading: boolean;
  error: string | null;
}

const initialState: ChatbotState = {
  messages: [],
  loading: false,
  error: null,
};

const chatbotSlice = createSlice({
  name: 'chatbot',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const { addMessage, setLoading, setError } = chatbotSlice.actions;
export default chatbotSlice.reducer;
