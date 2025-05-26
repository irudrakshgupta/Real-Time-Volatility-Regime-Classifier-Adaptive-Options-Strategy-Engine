import React, { useState } from 'react';
import { useMutation } from 'react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = 'http://localhost:8000/api/v1';

interface BacktestParams {
  strategy_type: string;
  days: number;
  expiration_days: number;
  strike_percentage: number;
  position_size: number;
}

const Backtest: React.FC = () => {
  const [params, setParams] = useState<BacktestParams>({
    strategy_type: 'calendar_spread',
    days: 30,
    expiration_days: 30,
    strike_percentage: 100,
    position_size: 1,
  });

  const backtestStrategy = useMutation(async (backtestParams: BacktestParams) => {
    const response = await axios.get(`${API_BASE_URL}/strategy/backtest`, {
      params: backtestParams,
    });
    return response.data;
  });

  const handleParamChange = (param: keyof BacktestParams) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    setParams({
      ...params,
      [param]: event.target.value,
    });
  };

  const handleBacktest = () => {
    backtestStrategy.mutate(params);
  };

  const strategyTypes = [
    { value: 'calendar_spread', label: 'Calendar Spread' },
    { value: 'butterfly', label: 'Iron Butterfly' },
    { value: 'straddle', label: 'Long Straddle' },
    { value: 'iron_condor', label: 'Iron Condor' },
    { value: 'backspread', label: 'Ratio Back Spread' },
  ];

  const chartData = backtestStrategy.data
    ? {
        labels: backtestStrategy.data.pnl_series.map((p: any) =>
          new Date(p.timestamp).toLocaleDateString()
        ),
        datasets: [
          {
            label: 'Strategy P&L',
            data: backtestStrategy.data.pnl_series.map((p: any) => p.pnl),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
          },
        ],
      }
    : null;

  return (
    <Grid container spacing={3}>
      {/* Backtest Configuration */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Backtest Configuration
            </Typography>
            <Box mt={2}>
              <FormControl fullWidth margin="normal">
                <InputLabel>Strategy Type</InputLabel>
                <Select
                  value={params.strategy_type}
                  onChange={handleParamChange('strategy_type')}
                  label="Strategy Type"
                >
                  {strategyTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                fullWidth
                margin="normal"
                label="Backtest Period (Days)"
                type="number"
                value={params.days}
                onChange={handleParamChange('days')}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Option Expiration Days"
                type="number"
                value={params.expiration_days}
                onChange={handleParamChange('expiration_days')}
              />
              <TextField
                fullWidth
                margin="normal"
                label="Strike Percentage"
                type="number"
                value={params.strike_percentage}
                onChange={handleParamChange('strike_percentage')}
                helperText="Percentage of current price (e.g., 100 for ATM)"
              />
              <TextField
                fullWidth
                margin="normal"
                label="Position Size"
                type="number"
                value={params.position_size}
                onChange={handleParamChange('position_size')}
              />
              <Button
                fullWidth
                variant="contained"
                color="primary"
                onClick={handleBacktest}
                disabled={backtestStrategy.isLoading}
                sx={{ mt: 2 }}
              >
                {backtestStrategy.isLoading ? <CircularProgress size={24} /> : 'Run Backtest'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Backtest Results */}
      <Grid item xs={12} md={8}>
        {backtestStrategy.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Error running backtest. Please try again.
          </Alert>
        )}
        {backtestStrategy.data && (
          <Grid container spacing={2}>
            {/* P&L Chart */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Strategy Performance
                  </Typography>
                  <Box height={400}>
                    {chartData && (
                      <Line
                        data={chartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              position: 'top' as const,
                            },
                            title: {
                              display: false,
                            },
                          },
                          scales: {
                            y: {
                              beginAtZero: false,
                            },
                          },
                        }}
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Performance Metrics */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Performance Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Total Return
                      </Typography>
                      <Typography variant="h6">
                        ${backtestStrategy.data.summary_statistics.total_return.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Win Rate
                      </Typography>
                      <Typography variant="h6">
                        {(backtestStrategy.data.summary_statistics.win_rate * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Max Drawdown
                      </Typography>
                      <Typography variant="h6" color="error">
                        ${Math.abs(backtestStrategy.data.summary_statistics.max_drawdown).toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Sharpe Ratio
                      </Typography>
                      <Typography variant="h6">
                        {backtestStrategy.data.summary_statistics.sharpe_ratio.toFixed(2)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Grid>
    </Grid>
  );
};

export default Backtest; 