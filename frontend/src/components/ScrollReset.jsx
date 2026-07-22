import { useEffect } from "react";
import { useLocation } from "react-router-dom";

/**
 * Scrolls to the top of the page on every route change. React Router
 * doesn't do this automatically, so without it, navigating to a new
 * page keeps whatever scroll position the previous page was at
 */
export default function ScrollReset() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}