'use client'

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import Link from 'next/link'

export function TopPlayers() {
  const { data: leaderboard, isLoading, error } = useQuery({
    queryKey: ['leaderboard', 'month'],
    queryFn: () => apiClient.getLeaderboard('month'),
  })

  if (isLoading) return <LoadingSpinner />
  
  if (error) {
    return (
      <div className="text-center text-red-600">
        Failed to load top players
      </div>
    )
  }

  const players = leaderboard?.data?.leaderboard || []

  if (players.length === 0) {
    return (
      <div className="text-center text-gray-500">
        No player data available
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="text-sm text-gray-600 mb-4">
        Top performers this month
      </div>
      
      {players.slice(0, 5).map((player: any, index: number) => (
        <div key={player.player_id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className={`
              flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium
              ${index < 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-600'}
            `}>
              {player.rank}
            </div>
            <div>
              <Link 
                href={`/players/${player.player_id}`}
                className="text-sm font-medium text-gray-900 hover:text-bridge-primary"
              >
                {player.player_name}
              </Link>
              <div className="text-xs text-gray-500">
                #{player.player_number}
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-sm font-medium text-masterpoints">
              {player.total_points?.toFixed(2)} MP
            </div>
            <div className="text-xs text-gray-500">
              {player.events_played} events
            </div>
          </div>
        </div>
      ))}
      
      <div className="text-center">
        <Link 
          href="/leaderboard"
          className="text-sm text-bridge-primary hover:underline"
        >
          View full leaderboard →
        </Link>
      </div>
    </div>
  )
}