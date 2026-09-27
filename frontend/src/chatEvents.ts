/** Window event that opens the chat widget (fired by "Ask about this item" buttons). */
export const OPEN_CHAT_EVENT = 'cc:open-chat'

export function openChat(): void {
  window.dispatchEvent(new Event(OPEN_CHAT_EVENT))
}
