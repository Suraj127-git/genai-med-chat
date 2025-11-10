import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/authSlice';
import chatReducer from '../features/chatSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chat: chatReducer,
  },
});

export default store;