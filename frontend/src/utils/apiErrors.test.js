import assert from 'node:assert/strict';
import test from 'node:test';

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
  assert.ok(error instanceof ApiRequestError);
  assert.equal(error.stage, 'connect');
  assert.equal(error.technicalDetail, 'Access is denied.');

  const message = await describePrintError(error);
  assert.match(message, /Access is denied/);
  assert.match(message, /reference: deadbeef/);
  assert.match(message, /HTTP 503/);
});

test('network failures distinguish a stopped server from an API error', async () => {
  const message = await describePrintError(
    new TypeError('Failed to fetch'),
    async () => false,
  );
  assert.match(message, /server stopped responding/i);
  assert.doesNotMatch(message, /^Failed to fetch$/);
});

test('plain-text HTTP failures are still useful', async () => {
  const error = await apiErrorFromResponse({
    status: 500,
    text: async () => 'Internal Server Error',
  });
  assert.equal(error.message, 'Internal Server Error');
  assert.equal(error.status, 500);
});
