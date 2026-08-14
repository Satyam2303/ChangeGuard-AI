const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "ChangeGuard request failed");
  return body;
}

export const api = {
  listChanges: () => request("/api/changes"),
  createChange: (changeRequest) =>
    request("/api/changes", {
      method: "POST",
      body: JSON.stringify({ request: changeRequest }),
    }),
  validateChange: (id) => request(`/api/changes/${id}/validate`, { method: "POST" }),
  decide: (id, decision) =>
    request(`/api/changes/${id}/${decision}`, {
      method: "POST",
      body: JSON.stringify({
        reviewer: "Human Reviewer",
        rationale: `Human reviewer ${decision}ed after inspecting Daytona evidence.`,
      }),
    }),
};

