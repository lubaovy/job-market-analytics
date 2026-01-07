import React, { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import jobs from "../data/jobs.json";


const JobDashboard = () => {
    const [selectedPlatform, setSelectedPlatform] = useState('all');
    const [selectedLocation, setSelectedLocation] = useState('all');

    // Process data based on filters
    const filteredJobs = useMemo(() => {
        return jobs.filter(job => {
            const platformMatch = selectedPlatform === 'all' || job.platform === selectedPlatform;
            const locationMatch = selectedLocation === 'all' ||
                job.location.toLowerCase().includes(selectedLocation.toLowerCase());
            return platformMatch && locationMatch;
        });
    }, [selectedPlatform, selectedLocation]);

    // Calculate top skills
    const skillCounts = useMemo(() => {
        const counts = {};
        filteredJobs.forEach(job => {
            job.skills.forEach(skill => {
                counts[skill] = (counts[skill] || 0) + 1;
            });
        });
        return Object.entries(counts)
            .map(([skill, count]) => ({ skill, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 20);
    }, [filteredJobs]);

    // Platform distribution
    const platformData = useMemo(() => {
        const counts = { itviec: 0, topcv: 0, vietnamworks: 0 };
        filteredJobs.forEach(job => {
            counts[job.platform]++;
        });
        return [
            { name: 'ITviec', value: counts.itviec, color: '#3b82f6' },
            { name: 'TopCV', value: counts.topcv, color: '#8b5cf6' },
            { name: 'VietnamWorks', value: counts.vietnamworks, color: '#ec4899' }
        ];
    }, [filteredJobs]);

    // Location distribution
    const locationData = useMemo(() => {
        const counts = {};
        filteredJobs.forEach(job => {
            const city = job.location.includes('Hà Nội') || job.location.includes('Ha Noi') ? 'Hanoi' :
                job.location.includes('Hồ Chí Minh') ? 'Ho Chi Minh' :
                    job.location.includes('Cần Thơ') ? 'Can Tho' : 'Others';
            counts[city] = (counts[city] || 0) + 1;
        });
        return Object.entries(counts).map(([city, count]) => ({ city, count }));
    }, [filteredJobs]);

    // Skill categories
    const skillCategories = useMemo(() => {
        const languages = ['Python', 'Java', 'TypeScript', 'JavaScript', 'Golang', 'SQL'];
        const frameworks = ['Flutter', 'React', 'Cypress', 'Playwright', 'Selenium', 'Appium'];
        const tools = ['Git', 'Docker', 'Kubernetes', 'Jira', 'Azure DevOps', 'GitHub'];
        const cloud = ['AWS', 'Azure', 'GCP', 'Cloud Security'];

        const countCategory = (categorySkills) => {
            return skillCounts
                .filter(s => categorySkills.some(cs => s.skill.toLowerCase().includes(cs.toLowerCase())))
                .reduce((sum, s) => sum + s.count, 0);
        };

        return [
            { category: 'Languages', count: countCategory(languages) },
            { category: 'Frameworks', count: countCategory(frameworks) },
            { category: 'Tools', count: countCategory(tools) },
            { category: 'Cloud', count: countCategory(cloud) }
        ];
    }, [skillCounts]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-slate-800 mb-2">
                        Vietnam Tech Job Market Analysis
                    </h1>
                    <p className="text-slate-600">
                        Real-time analysis of {filteredJobs.length} tech job postings • January 2025
                    </p>
                </div>

                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <div className="text-3xl font-bold text-blue-600">{filteredJobs.length}</div>
                        <div className="text-slate-600 text-sm mt-1">Total Jobs</div>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <div className="text-3xl font-bold text-purple-600">{skillCounts.length}</div>
                        <div className="text-slate-600 text-sm mt-1">Unique Skills</div>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <div className="text-3xl font-bold text-pink-600">3</div>
                        <div className="text-slate-600 text-sm mt-1">Platforms</div>
                    </div>
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <div className="text-3xl font-bold text-emerald-600">{locationData.length}</div>
                        <div className="text-slate-600 text-sm mt-1">Cities</div>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200 mb-8">
                    <div className="flex flex-wrap gap-4">
                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-sm font-medium text-slate-700 mb-2">Platform</label>
                            <select
                                value={selectedPlatform}
                                onChange={(e) => setSelectedPlatform(e.target.value)}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="all">All Platforms</option>
                                <option value="itviec">ITviec</option>
                                <option value="topcv">TopCV</option>
                                <option value="vietnamworks">VietnamWorks</option>
                            </select>
                        </div>
                        <div className="flex-1 min-w-[200px]">
                            <label className="block text-sm font-medium text-slate-700 mb-2">Location</label>
                            <select
                                value={selectedLocation}
                                onChange={(e) => setSelectedLocation(e.target.value)}
                                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="all">All Locations</option>
                                <option value="hanoi">Hanoi</option>
                                <option value="ho chi minh">Ho Chi Minh</option>
                                <option value="can tho">Can Tho</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
                    {/* Top Skills - Takes 2 columns */}
                    <div className="lg:col-span-2 bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <h2 className="text-xl font-bold text-slate-800 mb-4">
                            Top 20 Skills by Demand
                        </h2>
                        <ResponsiveContainer width="100%" height={500}>
                            <BarChart data={skillCounts} layout="vertical" margin={{ left: 100 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                <XAxis type="number" />
                                <YAxis dataKey="skill" type="category" width={90} style={{ fontSize: '12px' }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: 'white' }}
                                />
                                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Platform Distribution */}
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <h2 className="text-xl font-bold text-slate-800 mb-4">Platform Distribution</h2>
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie
                                    data={platformData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {platformData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="mt-4 space-y-2">
                            {platformData.map((item) => (
                                <div key={item.name} className="flex justify-between items-center">
                                    <div className="flex items-center">
                                        <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }}></div>
                                        <span className="text-sm text-slate-600">{item.name}</span>
                                    </div>
                                    <span className="text-sm font-semibold text-slate-800">{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Secondary Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Location Distribution */}
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <h2 className="text-xl font-bold text-slate-800 mb-4">Jobs by Location</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={locationData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                <XAxis dataKey="city" />
                                <YAxis />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: 'white' }}
                                />
                                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Skill Categories */}
                    <div className="bg-white rounded-xl p-6 shadow-lg border border-slate-200">
                        <h2 className="text-xl font-bold text-slate-800 mb-4">Skill Categories</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={skillCategories}>
                                <PolarGrid stroke="#e2e8f0" />
                                <PolarAngleAxis dataKey="category" />
                                <PolarRadiusAxis />
                                <Radar name="Demand" dataKey="count" stroke="#ec4899" fill="#ec4899" fillOpacity={0.6} />
                                <Tooltip />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Key Insights */}
                <div className="mt-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 shadow-lg text-white">
                    <h2 className="text-2xl font-bold mb-4">📊 Key Insights</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                            <div className="text-3xl mb-2">🔥</div>
                            <div className="font-semibold mb-1">Most In-Demand</div>
                            <div className="text-sm opacity-90">
                                {skillCounts[0]?.skill || 'N/A'} leads with {skillCounts[0]?.count || 0} mentions
                            </div>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                            <div className="text-3xl mb-2">🌍</div>
                            <div className="font-semibold mb-1">Top Location</div>
                            <div className="text-sm opacity-90">
                                {locationData[0]?.city || 'N/A'} has {locationData[0]?.count || 0} openings
                            </div>
                        </div>
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                            <div className="text-3xl mb-2">💼</div>
                            <div className="font-semibold mb-1">Data Source</div>
                            <div className="text-sm opacity-90">
                                Snapshot from Jan 6, 2025
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center text-slate-600 text-sm">
                    <p>Data scraped from ITviec, TopCV, and VietnamWorks • Built with React & Recharts</p>
                    <p className="mt-2">
                        <strong>Note:</strong> This is a demo with 6 sample jobs. Replace with your full 1500 records for complete analysis.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default JobDashboard;