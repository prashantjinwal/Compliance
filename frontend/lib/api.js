export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export function getAccessToken() {
  if (typeof window === "undefined") {
    return null;
  }

  return localStorage.getItem("access_token");
}

export function clearAuthTokens() {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function getApiErrorMessage(data, fallbackMessage) {
  if (!data) {
    return fallbackMessage;
  }

  if (typeof data === "string") {
    if (looksLikeHtml(data)) {
      return fallbackMessage;
    }

    if (data.includes("GEMINI_API_KEY")) {
      return "Backend AI configuration is missing. Please set GEMINI_API_KEY.";
    }

    return data;
  }

  if (typeof data.detail === "string") {
    if (looksLikeHtml(data.detail)) {
      return fallbackMessage;
    }

    if (data.detail.includes("GEMINI_API_KEY")) {
      return "Backend AI configuration is missing. Please set GEMINI_API_KEY.";
    }

    return data.detail;
  }

  if (typeof data.error === "string") {
    return data.error;
  }

  if (typeof data.message === "string") {
    return data.message;
  }

  const fieldErrors = Object.entries(data)
    .map(function ([key, value]) {
      if (Array.isArray(value)) {
        return key + ": " + value.join(", ");
      }

      if (typeof value === "string") {
        return key + ": " + value;
      }

      return "";
    })
    .filter(Boolean);

  if (fieldErrors.length > 0) {
    return fieldErrors.join(" | ");
  }

  return fallbackMessage;
}

function looksLikeHtml(value) {
  return typeof value === "string" && /<(?:!doctype|html|head|body|div|script)\b/i.test(value);
}

export async function parseApiResponse(response) {
  const responseText = await response.text();

  if (!responseText) {
    return null;
  }

  try {
    return JSON.parse(responseText);
  } catch (parseError) {
    return {
      detail: responseText,
    };
  }
}

export async function apiRequest(path, options) {
  const requestOptions = options || {};
  const headers = {
    ...(requestOptions.headers || {}),
  };

  if (requestOptions.body && !(requestOptions.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
  }

  const response = await fetch(API_BASE + path, {
    ...requestOptions,
    headers,
  });

  const data = await parseApiResponse(response);

  if (!response.ok) {
    let fallbackMessage = "Request failed.";

    if (response.status >= 500) {
      fallbackMessage = "The backend returned an unexpected server error.";
    }

    const error = new Error(getApiErrorMessage(data, fallbackMessage));
    error.status = response.status;
    error.data = data;
    error.path = path;
    throw error;
  }

  return data;
}

export async function authApiRequest(path, options) {
  const token = getAccessToken();
  const requestOptions = options || {};

  return apiRequest(path, {
    ...requestOptions,
    headers: {
      ...(requestOptions.headers || {}),
      ...(token ? { Authorization: "Bearer " + token } : {}),
    },
  });
}

export async function optionalAuthApiRequest(paths, options) {
  const candidates = Array.isArray(paths) ? paths : [paths];
  let lastNotFoundError = null;

  for (const path of candidates) {
    try {
      const data = await authApiRequest(path, options);
      return {
        data,
        path,
      };
    } catch (error) {
      if (error.status === 404) {
        lastNotFoundError = error;
        continue;
      }

      throw error;
    }
  }

  return {
    data: null,
    path: null,
    error: lastNotFoundError,
  };
}

export function fetchCurrentUser() {
  return authApiRequest("/api/auth/me/");
}

export function fetchOrganization() {
  return authApiRequest("/api/auth/organization/");
}

export function updateOrganization(payload) {
  return authApiRequest("/api/auth/organization/", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function fetchDashboardSummary() {
  return authApiRequest("/api/tasks/dashboard/");
}

export function fetchTasks(params) {
  const query = new URLSearchParams();

  if (params) {
    Object.entries(params).forEach(function ([key, value]) {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, value);
      }
    });
  }

  const suffix = query.toString() ? "?" + query.toString() : "";
  return authApiRequest("/api/tasks/" + suffix);
}

export function fetchRisks(params) {
  const query = new URLSearchParams();

  if (params) {
    Object.entries(params).forEach(function ([key, value]) {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, value);
      }
    });
  }

  const suffix = query.toString() ? "?" + query.toString() : "";
  return authApiRequest("/api/risks/" + suffix);
}

export async function uploadCopilotDocument(payload) {
  const formData = new FormData();

  if (payload && payload.file) {
    formData.append("file", payload.file);
  }

  if (payload && payload.text) {
    formData.append("text", payload.text);
  }

  return authApiRequest("/api/copilot/upload/", {
    method: "POST",
    body: formData,
  });
}

export function chatWithCopilotDocument(documentId, payload) {
  return authApiRequest("/api/copilot/chat/" + documentId + "/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getUserDisplayName(user) {
  if (user && user.full_name) {
    return user.full_name;
  }

  if (user && user.email) {
    return user.email.split("@")[0];
  }

  return "User";
}

export function getUserRole(user) {
  if (user && user.role && user.role.name) {
    return user.role.name;
  }

  return "Compliance Officer";
}

export function getUserInitial(user) {
  return getUserDisplayName(user).charAt(0).toUpperCase();
}

export function getOrganizationName(user) {
  if (user && user.organization && user.organization.name) {
    return user.organization.name;
  }

  return "Organization";
}

export function getSafeOrganizationValue(value) {
  if (!value || value === "Not specified") {
    return "";
  }

  return value;
}
