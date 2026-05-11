export function useAdminAuth() {
  const token = localStorage.getItem("admin_token");
  const isAuthed = Boolean(token);
  return { isAuthed };
}
