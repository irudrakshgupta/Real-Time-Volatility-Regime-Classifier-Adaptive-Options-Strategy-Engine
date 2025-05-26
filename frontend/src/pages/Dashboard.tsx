import React from 'react';
import { useQuery } from 'react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
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

// Register ChartJS components
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

interface MarketData {
  timestamp: string;
  close: number;
  vix: number;
  realized_vol: number;
  implied_vol_atm: number;
  regime: string;
  regime_probability: number;
}

const Dashboard: React.FC = () => {
  // Fetch current market data
  const { data: currentData, isLoading: isLoadingCurrent, error: currentError } = useQuery(
    'currentMarketData',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/market-data/current`);
      return response.data;
    },
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  // Fetch historical data
  const { data: historicalData, isLoading: isLoadingHistorical, error: historicalError } = useQuery(
    'historicalMarketData',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/market-data/historical`);
      return response.data;
    }
  );

  // Fetch strategy recommendations
  const { data: recommendations, isLoading: isLoadingRecommendations, error: recommendationsError } = useQuery(
    'recommendations',
    async () => {
      const response = await axios.get(`${API_BASE_URL}/strategy/recommend`);
      return response.data;
    }
  );

  if (isLoadingCurrent || isLoadingHistorical || isLoadingRecommendations) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (currentError || historicalError || recommendationsError) {
    return (
      <Alert severity="error">
        Error loading dashboard data. Please try again later.
      </Alert>
    );
  }

  const chartData = {
    labels: historicalData?.map((d: MarketData) => 
      new Date(d.timestamp).toLocaleDateString()
    ) || [],
    datasets: [
      {
        label: 'VIX',
        data: historicalData?.map((d: MarketData) => d.vix) || [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Realized Volatility',
        data: historicalData?.map((d: MarketData) => d.realized_vol) || [],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };

  return (
    <Grid container spacing={3}>
      {/* Current Market State */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Current Market State
            </Typography>
            <Typography variant="h6" color="primary">
              Regime: {currentData?.regime}
            </Typography>
            <Grid container spacing={2} mt={1}>
              <Grid item xs={3}>
                <Typography variant="body2" color="textSecondary">
                  VIX
                </Typography>
                <Typography variant="h6">
                  {currentData?.market_data.vix.toFixed(2)}%
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="body2" color="textSecondary">
                  Realized Volatility
                </Typography>
                <Typography variant="h6">
                  {currentData?.market_data.realized_vol.toFixed(2)}%
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="body2" color="textSecondary">
                  Implied Volatility (ATM)
                </Typography>
                <Typography variant="h6">
                  {currentData?.market_data.implied_vol_atm.toFixed(2)}%
                </Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography variant="body2" color="textSecondary">
                  IV Skew
                </Typography>
                <Typography variant="h6">
                  {currentData?.market_data.skew.toFixed(2)}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Volatility Chart */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Historical Volatility
            </Typography>
            <Box height={400}>
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
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Strategy Recommendations */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Recommended Strategies
            </Typography>
            <Grid container spacing={2}>
              {recommendations?.recommendations.map((strategy: any, index: number) => (
                <Grid item xs={12} md={4} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" color="primary">
                        {strategy.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        {strategy.description}
                      </Typography>
                      <Typography variant="body2">
                        Risk Profile: {strategy.risk_profile}
                      </Typography>
                      <Typography variant="body2">
                        Duration: {strategy.duration}
                      </Typography>
                      <Typography variant="body2">
                        Score: {(strategy.score * 100).toFixed(1)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default Dashboard; 