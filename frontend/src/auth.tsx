import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { ApiError, fetchMe, loginUser, registerUser, type RegisterInput } from './api'
import type { User } from './types'

const TOKEN_KEY = 'cc_token'

interface AuthContextValue {
  user: User | null
  token: string | null
  ready: boolean
  login: (email: string, password: string) => Promise<User>
  register: (input: RegisterInput) => Promise<User>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [ready, setReady] = useState(false)

  // On page load, check that a saved token is still valid.
  useEffect(() => {
    if (!token) {
      setReady(true)
      return
    }
    fetchMe(token)
      .then(setUser)
      .catch((err) => {
        // Only a rejected token logs the user out; a server that's briefly down doesn't.
        if (err instanceof ApiError && err.status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          setToken(null)
        }
      })
      .finally(() => setReady(true))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function save(auth: { token: string; user: User }): User {
    localStorage.setItem(TOKEN_KEY, auth.token)
    setToken(auth.token)
    setUser(auth.user)
    return auth.user
  }

  const value: AuthContextValue = {
    user,
    token,
    ready,
    login: async (email, password) => save(await loginUser(email, password)),
    register: async (input) => save(await registerUser(input)),
    logout: () => {
      localStorage.removeItem(TOKEN_KEY)
      setToken(null)
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
