import chatReducer, { addMessage, sendChatQuery } from '../packages/store/src/features/chatSlice';

describe('chatSlice', () => {
  it('addMessage appends a message', () => {
    const state = chatReducer(undefined, { type: '@@INIT' });
    const next = chatReducer(state, addMessage({ sender: 'user', content: 'Hello' }));
    expect(next.messages).toHaveLength(1);
    expect(next.messages[0]).toEqual({ sender: 'user', content: 'Hello' });
  });

  it('sendChatQuery.fulfilled adds bot reply and sets conv_id', () => {
    const state = chatReducer(undefined, { type: '@@INIT' });
    const payload = { answer: 'Hi there', conv_id: 42 };
    const next = chatReducer(state, { type: sendChatQuery.fulfilled.type, payload });
    expect(next.messages).toHaveLength(1);
    expect(next.messages[0]).toEqual({ sender: 'bot', content: 'Hi there' });
    expect(next.lastConvId).toBe(42);
    expect(next.loading).toBe(false);
  });
});