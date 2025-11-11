/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setupTests.js'],
  transform: {
    '^.+\\.[jt]sx?$': 'babel-jest',
  },
  moduleNameMapper: {
    '^@genai-med-chat/shared$': '<rootDir>/packages/shared/src',
    '^@genai-med-chat/auth$': '<rootDir>/packages/auth/src',
    '^@genai-med-chat/chat$': '<rootDir>/packages/chat/src',
    '^@genai-med-chat/store$': '<rootDir>/packages/store/src',
    '^gsap$': '<rootDir>/tests/__mocks__/gsap.js',
    '\\.(css|less|scss)$': 'identity-obj-proxy'
  },
  testMatch: ['**/tests/**/*.(test|spec).(js|jsx)'],
  extensionsToTreatAsEsm: ['.ts', '.tsx', '.jsx'],
};