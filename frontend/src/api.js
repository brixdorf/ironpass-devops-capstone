// Small wrapper around fetch. All calls go to /api and nginx or Ingress routes them.
async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join(", ")
      : data.detail;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }
  return data;
}

export const api = {
  stats: () => request("/stats"),
  plans: () => request("/plans"),
  members: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== "" && value !== null && value !== undefined) query.set(key, value);
    });
    const suffix = query.toString() ? `?${query}` : "";
    return request(`/members${suffix}`);
  },
  createMember: (body) => request("/members", { method: "POST", body: JSON.stringify(body) }),
  updateMember: (id, body) =>
    request(`/members/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  renewMember: (id) => request(`/members/${id}/renew`, { method: "POST" }),
  deleteMember: (id) => request(`/members/${id}`, { method: "DELETE" }),
  activity: () => request("/activity?limit=8"),
  checkIn: (memberId) =>
    request("/checkins", { method: "POST", body: JSON.stringify({ member_id: memberId }) }),
};
