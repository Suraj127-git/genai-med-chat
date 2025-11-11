import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

// Chat Service endpoints are proxied by gateway at /chat/* or directly /api/v1/* in dev
export const sendChatQuery = createAsyncThunk(
  'chat/sendChatQuery',
  async ({ user_id, text, conv_id }, { rejectWithValue }) => {
    try {
      const res = await axios.post('/api/v1/chat/query', { user_id, text, conv_id });
      return res.data; // { answer, conv_id }
    } catch (e) {
      return rejectWithValue(e.message);
    }
  }
);

export const fetchGraph = createAsyncThunk('chat/fetchGraph', async (conv_id, { rejectWithValue }) => {
  try {
    const res = await axios.get(`/api/v1/graph/${conv_id}`);
    return res.data; // { nodes, edges }
  } catch (e) {
    return rejectWithValue(e.message);
  }
});

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    lastConvId: null,
    graph: null,
    loading: false,
    error: null,
  },
  reducers: {
    addMessage(state, action) {
      const { sender, content } = action.payload;
      state.messages.push({ sender, content });
    },
    clearChat(state) {
      state.messages = [];
      state.lastConvId = null;
      state.graph = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatQuery.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(sendChatQuery.fulfilled, (state, action) => {
        state.loading = false;
        const { answer, conv_id } = action.payload;
        // push bot reply; user message is pushed from UI dispatch below as a separate action
        state.lastConvId = conv_id;
        state.messages.push({ sender: 'bot', content: answer });
      })
      .addCase(sendChatQuery.rejected, (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(fetchGraph.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchGraph.fulfilled, (state, action) => { state.loading = false; state.graph = action.payload; })
      .addCase(fetchGraph.rejected, (state, action) => { state.loading = false; state.error = action.payload; });
  }
});

export const { addMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
