// Type guard to check if error has a detail property
export function hasDetailProperty(error: unknown): error is { detail: string } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'detail' in error &&
    typeof (error as { detail: unknown }).detail === 'string'
  )
}

// Type guard to check if error has a message property
export function hasMessageProperty(error: unknown): error is { message: string } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as { message: unknown }).message === 'string'
  )
}

// Type guard for response data errors
export function hasResponseData(error: unknown): error is { response: { data: { detail: string } } } {
  return (
    typeof error === 'object' &&
    error !== null &&
    'response' in error &&
    typeof (error as { response: unknown }).response === 'object' &&
    (error as { response: object }).response !== null &&
    'data' in (error as { response: object }).response &&
    typeof ((error as { response: { data: unknown } }).response.data) === 'object' &&
    ((error as { response: { data: object } }).response.data) !== null &&
    'detail' in ((error as { response: { data: object } }).response.data) &&
    typeof ((error as { response: { data: { detail: unknown } } }).response.data.detail) === 'string'
  )
}

// Helper to extract error message
export function getErrorMessage(error: unknown, fallback = 'An error occurred'): string {
  if (hasResponseData(error)) {
    return error.response.data.detail
  }
  if (hasDetailProperty(error)) {
    return error.detail
  }
  if (hasMessageProperty(error)) {
    return error.message
  }
  return fallback
}
