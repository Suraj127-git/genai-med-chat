import authReducer, { logout, loginUser } from '../packages/store/src/features/authSlice';

jest.mock('@genai-med-chat/shared', () => ({
  removeItem: jest.fn(),
  setItem: jest.fn(),
  getItem: jest.fn(),
  apiClient: { post: jest.fn(), get: jest.fn() }
}));

import { removeItem } from '@genai-med-chat/shared';

describe('authSlice', () => {
  const initial = { user: null, loading: false, error: null };

  it('handles loginUser.fulfilled by setting user', () => {
    const user = { id: 1, email: 'user@example.com' };
    const state = authReducer(initial, { type: loginUser.fulfilled.type, payload: user });
    expect(state.user).toEqual(user);
    expect(state.loading).toBe(false);
  });

  it('handles logout by clearing user and removing token', () => {
    const loggedIn = { user: { id: 1 }, loading: false, error: null };
    const state = authReducer(loggedIn, logout());
    expect(state.user).toBeNull();
    expect(removeItem).toHaveBeenCalledWith('token');
  });
});