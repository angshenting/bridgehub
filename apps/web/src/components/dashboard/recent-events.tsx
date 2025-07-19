'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import Link from 'next/link'

export function RecentEvents() {
  const { data: events, isLoading, error } = useQuery({
    queryKey: ['recent-events'],
    queryFn: () => apiClient.getRecentEvents(30),
  })

  if (isLoading) return <LoadingSpinner />
  
  if (error) {
    return (
      <div className="text-center text-red-600">
        Failed to load recent events
      </div>
    )
  }

  const eventsList = events?.data || []

  if (eventsList.length === 0) {
    return (
      <div className="text-center text-gray-500">
        No recent events found
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {eventsList.slice(0, 5).map((event: { id: number; name: string; date: string; start_date: string; type: string; status: string }) => (
        <div key={event.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div className="flex-1">
            <Link 
              href={`/events/${event.id}`}
              className="text-sm font-medium text-gray-900 hover:text-bridge-primary"
            >
              {event.name}
            </Link>
            <div className="flex items-center mt-1 space-x-2">
              <span className="text-xs text-gray-500">
                {new Date(event.start_date).toLocaleDateString()}
              </span>
              <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                {event.type}
              </span>
              <span className={`text-xs px-2 py-1 rounded-full ${
                event.status === 'completed' ? 'bg-green-100 text-green-800' :
                event.status === 'active' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {event.status}
              </span>
            </div>
          </div>
          <div className="text-right">
            <Link 
              href={`/events/${event.id}/results`}
              className="text-xs text-bridge-primary hover:underline"
            >
              View Results
            </Link>
          </div>
        </div>
      ))}
      
      {eventsList.length > 5 && (
        <div className="text-center">
          <Link 
            href="/events"
            className="text-sm text-bridge-primary hover:underline"
          >
            View all events →
          </Link>
        </div>
      )}
    </div>
  )
}