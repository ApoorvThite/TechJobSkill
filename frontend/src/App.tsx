import { useEffect, useState } from 'react'
import OverviewPage from './pages/OverviewPage'
import SkillTrendsPage from './pages/SkillTrendsPage'
import RisingSkillsPage from './pages/RisingSkillsPage'
import RoleClustersPage from './pages/RoleClustersPage'

export default function App() {
  const [route, setRoute] = useState(window.location.hash || '#/overview')
  useEffect(() => {
    const onHashChange = () => setRoute(window.location.hash || '#/overview')
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])
  return (
    <div>
      <nav style={{ display: 'flex', gap: 12, padding: 12, borderBottom: '1px solid #eee' }}>
        <a href="#/overview">Overview</a>
        <a href="#/skills">Skill Trends</a>
        <a href="#/rising">Rising Skills</a>
        <a href="#/clusters">Role Clusters</a>
      </nav>
      {route === '#/overview' && <OverviewPage />}
      {route === '#/skills' && <SkillTrendsPage />}
      {route === '#/rising' && <RisingSkillsPage />}
      {route === '#/clusters' && <RoleClustersPage />}
    </div>
  )
}
