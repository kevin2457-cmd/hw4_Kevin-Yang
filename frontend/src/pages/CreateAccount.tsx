import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import AuthLayout from '../components/AuthLayout'
import FormField from '../components/FormField'

const MIN_PASSWORD_LENGTH = 8

const EMPTY = { firstName: '', lastName: '', email: '', password: '', confirmPassword: '' }

function validate(f: typeof EMPTY): string | null {
  const missing = [
    !f.firstName.trim() && 'first name',
    !f.lastName.trim() && 'last name',
    !f.email.trim() && 'email',
    !f.password && 'password',
  ].filter(Boolean)
  if (missing.length) {
    const list = missing.length > 1 ? `${missing.slice(0, -1).join(', ')} and ${missing.at(-1)}` : missing[0]
    return `Please enter your ${list}.`
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email.trim())) return 'Please enter a valid email address.'
  if (f.password.length < MIN_PASSWORD_LENGTH) return `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`
  if (f.password !== f.confirmPassword) return 'Passwords do not match.'
  return null
}

export default function CreateAccount() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const set = (key: keyof typeof EMPTY) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const problem = validate(form)
    if (problem) {
      setError(problem)
      return
    }
    setError(null)
    setSubmitting(true)
    try {
      await register({
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      navigate('/')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout>
      <form className="auth-card" onSubmit={handleSubmit} noValidate>
        <h1>Create account</h1>
        <p className="muted">Join Campus Customs to save your shopping chats.</p>
        <div className="form-row">
          <FormField label="First name" name="firstName" autoComplete="given-name" value={form.firstName} onChange={set('firstName')} />
          <FormField label="Last name" name="lastName" autoComplete="family-name" value={form.lastName} onChange={set('lastName')} />
        </div>
        <FormField label="Email" name="email" type="email" autoComplete="email" value={form.email} onChange={set('email')} />
        <FormField
          label="Password"
          name="password"
          type="password"
          autoComplete="new-password"
          placeholder={`At least ${MIN_PASSWORD_LENGTH} characters`}
          value={form.password}
          onChange={set('password')}
        />
        <FormField
          label="Confirm password"
          name="confirmPassword"
          type="password"
          autoComplete="new-password"
          value={form.confirmPassword}
          onChange={set('confirmPassword')}
        />
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" className="btn btn-block" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Create account'}
        </button>
        <p className="muted small">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </AuthLayout>
  )
}
