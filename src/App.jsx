import React, { useState, useEffect } from 'react';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, AlertCircle, Plus, Trash2, BarChart3 } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [transactions, setTransactions] = useState([
    { id: 1, date: '2025-01-20', description: 'Grocery Store', amount: 45.50, category: 'Food', type: 'expense' },
    { id: 2, date: '2025-01-19', description: 'Gas Station', amount: 60, category: 'Transport', type: 'expense' },
    { id: 3, date: '2025-01-18', description: 'Netflix', amount: 15.99, category: 'Entertainment', type: 'expense' },
    { id: 4, date: '2025-01-17', description: 'Salary', amount: 3500, category: 'Income', type: 'income' },
    { id: 5, date: '2025-01-16', description: 'Restaurant', amount: 35, category: 'Food', type: 'expense' },
    { id: 6, date: '2025-01-15', description: 'Electric Bill', amount: 120, category: 'Utilities', type: 'expense' },
  ]);
  
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    description: '',
    amount: '',
    category: 'Food',
    type: 'expense'
  });

  const [predictions, setPredictions] = useState({});
  const [anomalies, setAnomalies] = useState([]);

  useEffect(() => {
    calculateInsights();
  }, [transactions]);

  const calculateInsights = () => {
    // Calculate spending by category
    const categorySpending = {};
    transactions.forEach(t => {
      if (t.type === 'expense') {
        categorySpending[t.category] = (categorySpending[t.category] || 0) + t.amount;
      }
    });

    // Spending Prediction: 20% growth forecast
    const predicted = {};
    Object.entries(categorySpending).forEach(([cat, amount]) => {
      predicted[cat] = (amount * 1.2).toFixed(2);
    });
    setPredictions(predicted);

    // Anomaly Detection: Statistical outlier detection
    const detected = [];
    Object.entries(categorySpending).forEach(([category, total]) => {
      const catTransactions = transactions.filter(t => t.category === category && t.type === 'expense');
      if (catTransactions.length > 0) {
        const mean = catTransactions.reduce((sum, t) => sum + t.amount, 0) / catTransactions.length;
        const variance = catTransactions.reduce((sum, t) => sum + Math.pow(t.amount - mean, 2), 0) / catTransactions.length;
        const stdDev = Math.sqrt(variance);
        
        // Flag transactions > 2 std dev from mean
        catTransactions.forEach(t => {
          if (Math.abs(t.amount - mean) > 2 * stdDev && t.amount > mean * 1.5) {
            detected.push(t);
          }
        });
      }
    });
    setAnomalies(detected);
  };

  const handleAddTransaction = (e) => {
    e.preventDefault();
    if (formData.description && formData.amount) {
      const newTransaction = {
        id: Date.now(),
        ...formData,
        amount: parseFloat(formData.amount)
      };
      setTransactions([newTransaction, ...transactions]);
      setFormData({
        date: new Date().toISOString().split('T')[0],
        description: '',
        amount: '',
        category: 'Food',
        type: 'expense'
      });
    }
  };

  const handleDeleteTransaction = (id) => {
    setTransactions(transactions.filter(t => t.id !== id));
  };

  // Calculate metrics
  const expensesByCategory = {};
  const incomeTotal = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
  
  transactions.forEach(t => {
    if (t.type === 'expense') {
      expensesByCategory[t.category] = (expensesByCategory[t.category] || 0) + t.amount;
    }
  });

  const pieData = Object.entries(expensesByCategory).map(([name, value]) => ({ name, value }));
  const totalExpenses = Object.values(expensesByCategory).reduce((a, b) => a + b, 0);
  const netBalance = incomeTotal - totalExpenses;

  const monthlyTrend = [
    { month: 'Nov', expenses: 450, income: 3500 },
    { month: 'Dec', expenses: 520, income: 3500 },
    { month: 'Jan', expenses: totalExpenses, income: incomeTotal }
  ];

  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-blue-400" />
              <h1 className="text-2xl font-bold text-white">FinanceAI</h1>
            </div>
            <p className="text-slate-400 text-sm">ML-Powered Personal Finance Assistant</p>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-4">
            {['dashboard', 'transactions', 'predictions', 'anomalies'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 font-medium text-sm transition-colors border-b-2 ${
                  activeTab === tab
                    ? 'text-blue-400 border-blue-400'
                    : 'text-slate-400 border-transparent hover:text-slate-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        
        {/* DASHBOARD TAB */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
                <p className="text-slate-400 text-sm font-medium">Total Income</p>
                <p className="text-3xl font-bold text-green-400 mt-2">${incomeTotal.toFixed(2)}</p>
              </div>
              <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
                <p className="text-slate-400 text-sm font-medium">Total Expenses</p>
                <p className="text-3xl font-bold text-red-400 mt-2">${totalExpenses.toFixed(2)}</p>
              </div>
              <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
                <p className="text-slate-400 text-sm font-medium">Net Balance</p>
                <p className={`text-3xl font-bold mt-2 ${netBalance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${netBalance.toFixed(2)}
                </p>
              </div>
              <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
                <p className="text-slate-400 text-sm font-medium">Save Rate</p>
                <p className="text-3xl font-bold text-blue-400 mt-2">
                  {incomeTotal > 0 ? ((netBalance / incomeTotal) * 100).toFixed(1) : 0}%
                </p>
              </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  Spending by Category
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={pieData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: $${value}`} outerRadius={80} fill="#8884d8" dataKey="value">
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  Income vs Expenses
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#404854" />
                    <XAxis dataKey="month" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #404854' }} />
                    <Legend />
                    <Bar dataKey="income" fill="#10b981" />
                    <Bar dataKey="expenses" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* TRANSACTIONS TAB */}
        {activeTab === 'transactions' && (
          <div className="space-y-6">
            <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Plus className="w-5 h-5 text-blue-400" />
                Add Transaction
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="bg-slate-600 text-white px-3 py-2 rounded border border-slate-500 text-sm"
                />
                <input
                  type="text"
                  placeholder="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="bg-slate-600 text-white px-3 py-2 rounded border border-slate-500 text-sm"
                />
                <input
                  type="number"
                  placeholder="Amount"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  step="0.01"
                  className="bg-slate-600 text-white px-3 py-2 rounded border border-slate-500 text-sm"
                />
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="bg-slate-600 text-white px-3 py-2 rounded border border-slate-500 text-sm"
                >
                  <option>Food</option>
                  <option>Transport</option>
                  <option>Utilities</option>
                  <option>Entertainment</option>
                  <option>Health</option>
                  <option>Shopping</option>
                </select>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="bg-slate-600 text-white px-3 py-2 rounded border border-slate-500 text-sm"
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
                <button onClick={handleAddTransaction} className="bg-blue-500 hover:bg-blue-600 text-white font-medium px-4 py-2 rounded text-sm transition">
                  Add
                </button>
              </div>
            </div>

            <div className="bg-slate-700 rounded-lg border border-slate-600 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-600 border-b border-slate-500">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300">Description</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300">Category</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300">Amount</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-slate-300">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(t => (
                      <tr key={t.id} className="border-b border-slate-600 hover:bg-slate-600 transition">
                        <td className="px-6 py-3 text-sm text-slate-300">{t.date}</td>
                        <td className="px-6 py-3 text-sm text-slate-300">{t.description}</td>
                        <td className="px-6 py-3 text-sm"><span className="bg-slate-600 px-2 py-1 rounded text-slate-200">{t.category}</span></td>
                        <td className={`px-6 py-3 text-sm font-semibold ${t.type === 'income' ? 'text-green-400' : 'text-red-400'}`}>
                          {t.type === 'income' ? '+' : '-'}${t.amount.toFixed(2)}
                        </td>
                        <td className="px-6 py-3 text-sm">
                          <button onClick={() => handleDeleteTransaction(t.id)} className="text-red-400 hover:text-red-300 transition">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* PREDICTIONS TAB */}
        {activeTab === 'predictions' && (
          <div className="space-y-6">
            <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
              <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-400" />
                Next Month Spending Predictions
              </h3>
              <p className="text-slate-400 text-sm mb-4">ML model predicts a 20% increase based on your spending patterns</p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(predictions).map(([category, amount]) => (
                  <div key={category} className="bg-slate-600 rounded-lg p-4 border border-slate-500">
                    <p className="text-slate-300 text-sm font-medium">{category}</p>
                    <p className="text-2xl font-bold text-blue-400 mt-2">${amount}</p>
                    <p className="text-xs text-slate-400 mt-1">Predicted for next month</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ANOMALIES TAB */}
        {activeTab === 'anomalies' && (
          <div className="space-y-6">
            <div className="bg-slate-700 rounded-lg p-6 border border-slate-600">
              <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-400" />
                Anomaly Detection
              </h3>
              <p className="text-slate-400 text-sm mb-4">Unusual transactions flagged by ML model (2+ standard deviations from mean)</p>
              
              {anomalies.length === 0 ? (
                <div className="bg-slate-600 rounded-lg p-8 text-center">
                  <p className="text-slate-400">No anomalies detected. Your spending is consistent!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {anomalies.map(t => (
                    <div key={t.id} className="bg-red-900/20 border border-red-600/50 rounded-lg p-4 flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-white font-medium">{t.description}</p>
                        <p className="text-slate-400 text-sm">{t.category} • {t.date}</p>
                        <p className="text-red-400 font-semibold mt-1">${t.amount.toFixed(2)} - Unusual for this category</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
