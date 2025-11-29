import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../../services/auth';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  // Rutas de autenticación que NUNCA requieren token (ni siquiera lo envían)
  const authRoutes = [
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/refresh'
  ];

  // Rutas de lectura pública que no requieren token (solo GET)
  // Excluir rutas protegidas como my-posts, me, etc.
  const publicReadRoutes = [
    '/api/categories',
    '/api/posts/' // Incluye /api/posts/ y /api/posts/?...
  ];
  
  // Rutas protegidas que SIEMPRE requieren autenticación (aunque sean GET)
  const protectedRoutes = [
    '/api/posts/posts/my-posts',
    '/api/posts/my-posts',
    '/api/users/me',
    '/api/users/me/'
  ];

  const isAuthRoute = authRoutes.some(route => req.url.includes(route));
  const isProtectedRoute = protectedRoutes.some(route => req.url.includes(route));
  const isPublicReadRoute = req.method === 'GET' && publicReadRoutes.some(route => req.url.includes(route)) && !isProtectedRoute;

  // Para rutas públicas o de autenticación, NO hacer nada (no enviar token, no limpiar)
  if (isAuthRoute || isPublicReadRoute) {
    // Simplemente pasar la petición sin modificar
    return next(req);
  }

  // Para rutas protegidas, verificar y enviar token si existe y es válido
  const token = authService.getToken();
  const isValidToken = authService.isTokenValid();

  if (token && isValidToken) {
    // Enviar token solo si es válido
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  } else if (token && !isValidToken) {
    // Si hay token pero es inválido, limpiarlo silenciosamente
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  return next(req).pipe(
    catchError(error => {
      // NO intentar refresh en rutas públicas o de autenticación
      if (isAuthRoute || isPublicReadRoute) {
        return throwError(() => error);
      }

      // Si es 401 en una ruta protegida y tenemos token válido, intentar refresh
      const currentToken = authService.getToken();
      const currentIsValidToken = authService.isTokenValid();
      
      if (error.status === 401 && currentToken && currentIsValidToken) {
        // Verificar si el error es por token inválido o expirado
        const errorMessage = error.error?.detail || error.error?.message || '';
        if (errorMessage.includes('token') || errorMessage.includes('Token') || errorMessage.includes('expired')) {
          // Intentar refresh token
          return authService.refreshToken().pipe(
            switchMap((response: any) => {
              const newToken = response.access;
              if (newToken) {
                localStorage.setItem('access_token', newToken);
                
                req = req.clone({
                  setHeaders: {
                    Authorization: `Bearer ${newToken}`
                  }
                });
                return next(req);
              }
              throw new Error('No se pudo obtener nuevo token');
            }),
            catchError(err => {
              // Si el refresh falla, limpiar tokens y redirigir
              authService.logout();
              return throwError(() => err);
            })
          );
        }
      }
      return throwError(() => error);
    })
  );
};
