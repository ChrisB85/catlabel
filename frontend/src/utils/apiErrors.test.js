import { expect, test } from 'vitest';

import {
  ApiRequestError,
  apiErrorFromResponse,
  describePrintError,
} from './apiErrors.js';

test('structured print errors retain the backend stage and cause', async () => {
  const response = {
    status: 503,
    text: async () => JSON.stringify({
      detail: {
        message: 'Could not connect to the printer.',
        stage: 'connect',
        error: 'Access is denied.',
        suggestion: 'Pair the printer first.',
        error_id: 'deadbeef',
      },
    }),
  };

  const error = await apiErrorFromResponse(response, 'Print failed');
  expect(error).toBeInstanceOf(ApiRequestError);
  expect(error.stage).toBe('connect');
  expect(error.technicalDetail).toBe('Access is denied.');

  const message = await describePrintError(error);
  expect(message).toMatch(/Access is denied/);
  expect(message).toMatch(/reference: deadbeef/);
  expect(message).toMatch(/HTTP 503/);
});

test('network failures distinguish a stopped server from an API error', async () => {
  const message = await describePrintError(
    new TypeError('Failed to fetch'),
    async () => false,
  );
  expect(message).toMatch(/server stopped responding/i);
  expect(message).not.toMatch(/^Failed to fetch$/);
});

test('plain-text HTTP failures are still useful', async () => {
  const error = await apiErrorFromResponse({
    status: 500,
    text: async () => 'Internal Server Error',
  });
  expect(error.message).toBe('Internal Server Error');
  expect(error.status).toBe(500);
});
