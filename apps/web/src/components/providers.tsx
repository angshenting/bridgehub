'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: (failureCount: number, error: unknown) => {
              // Don't retry on 4xx errors
              if (error && typeof error === 'object' && 'response' in error) {
                const axiosError = error as { response?: { status?: number } }
                if (axiosError.response?.status && axiosError.response.status >= 400 && axiosError.response.status < 500) {
                  return false
                }
              }
              return failureCount < 3
            },
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}