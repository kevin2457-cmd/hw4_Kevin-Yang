import { useEffect, useState } from 'react'

interface AsyncState<T> {
  data: T | null
  error: string | null
  loading: boolean
}

/** Run an async loader whenever `deps` change and track loading/error state. */
export function useAsync<T>(loader: () => Promise<T>, deps: unknown[]): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ data: null, error: null, loading: true })

  useEffect(() => {
    let cancelled = false
    setState({ data: null, error: null, loading: true })
    loader()
      .then((data) => !cancelled && setState({ data, error: null, loading: false }))
      .catch((err: Error) => !cancelled && setState({ data: null, error: err.message, loading: false }))
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}
