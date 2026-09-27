import type { InputHTMLAttributes } from 'react'

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  name: string
}

export default function FormField({ label, name, ...inputProps }: Props) {
  return (
    <label className="form-field" htmlFor={name}>
      <span>{label}</span>
      <input id={name} name={name} {...inputProps} />
    </label>
  )
}
