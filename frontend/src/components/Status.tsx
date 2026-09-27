export function Loading({ label = 'Loading…' }: { label?: string }) {
  return <p className="status muted">{label}</p>
}

export function ErrorMessage({ message }: { message: string }) {
  return (
    <p className="status error">Couldn't load data. {message}</p>
  )
}
