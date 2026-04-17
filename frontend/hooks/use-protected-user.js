"use client";

import { useEffect, useState } from "react";

import {
  clearAuthTokens,
  fetchCurrentUser,
  getAccessToken,
} from "@/lib/api";

export function useProtectedUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;
    const token = getAccessToken();

    if (!token) {
      window.location.href = "/auth";
      return undefined;
    }

    async function loadUser() {
      try {
        const currentUser = await fetchCurrentUser();

        if (!isActive) {
          return;
        }

        setUser(currentUser);
        setError("");
      } catch (requestError) {
        if (!isActive) {
          return;
        }

        if (requestError.status === 401 || requestError.status === 403) {
          clearAuthTokens();
          window.location.href = "/auth";
          return;
        }

        setError(requestError.message || "Unable to load user data.");
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      isActive = false;
    };
  }, []);

  return {
    user,
    loading,
    error,
    setUser,
  };
}
