import { useQuery } from '@tanstack/react-query';
import Layout from '../components/Layout';
import { progressApi } from '../services/progressApi';
import { Trophy, Crown, Medal, Zap } from 'lucide-react';

export default function LeaderboardPage() {
  const { data: leaderboard, isLoading } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => progressApi.getLeaderboard().then(r => r.data)
  });

  const rankIcon = (rank) => {
    if (rank === 1) return <Crown size={18} className="text-yellow-500" />;
    if (rank === 2) return <Medal size={18} className="text-slate-400" />;
    if (rank === 3) return <Medal size={18} className="text-amber-600" />;
    return <span className="text-sm font-bold text-slate-400 w-5 text-center">{rank}</span>;
  };

  return (
    <Layout title="Leaderboard">
      {/* Top 3 podium */}
      {leaderboard && leaderboard.length >= 3 && (
        <div className="flex items-end justify-center gap-4 mb-8">
          {[leaderboard[1], leaderboard[0], leaderboard[2]].map((entry, i) => {
            const heights = ['h-28', 'h-36', 'h-24'];
            const colors = ['bg-slate-100', 'bg-gradient-to-b from-yellow-400 to-amber-500', 'bg-amber-100'];
            const textColors = ['text-slate-700', 'text-white', 'text-amber-800'];
            return (
              <div key={entry.user_id} className={`flex flex-col items-center ${heights[i]} justify-end pb-3 px-4 rounded-t-xl ${colors[i]} min-w-[100px]`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm mb-2 ${i === 1 ? 'bg-white text-amber-600' : 'bg-indigo-100 text-indigo-700'}`}>
                  {entry.full_name?.[0]?.toUpperCase()}
                </div>
                <p className={`text-xs font-semibold ${textColors[i]} truncate max-w-[80px] text-center`}>{entry.full_name}</p>
                <p className={`text-xs ${textColors[i]} opacity-80`}>{entry.total_xp} XP</p>
                <div className="mt-1">{rankIcon(entry.rank)}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Full list */}
      <div className="bg-white rounded-xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center gap-2">
          <Trophy size={16} className="text-amber-500" />
          <h2 className="font-semibold text-slate-900">Rankings</h2>
        </div>
        {isLoading ? (
          <div className="flex justify-center py-10">
            <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="divide-y divide-slate-50">
            {leaderboard?.map(entry => (
              <div key={entry.user_id}
                className={`flex items-center gap-4 px-5 py-4 ${entry.is_current_user ? 'bg-indigo-50' : 'hover:bg-slate-50'} transition-colors`}>
                <div className="w-8 flex items-center justify-center">{rankIcon(entry.rank)}</div>
                <div className="w-9 h-9 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-700 font-semibold text-sm flex-shrink-0">
                  {entry.full_name?.[0]?.toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`font-medium text-sm ${entry.is_current_user ? 'text-indigo-700' : 'text-slate-900'}`}>
                    {entry.full_name} {entry.is_current_user && '(You)'}
                  </p>
                  <p className="text-xs text-slate-400">@{entry.username} · {entry.rank_title}</p>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-amber-600 font-bold">
                    <Zap size={14} />
                    <span>{entry.total_xp}</span>
                  </div>
                  <p className="text-xs text-slate-400">Level {entry.level}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}


