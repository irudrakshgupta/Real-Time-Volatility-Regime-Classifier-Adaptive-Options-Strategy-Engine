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

interface StrategyParams {
  strategy_type: string;
  expiration_days: number;
  strike_percentage: number;
  position_size: number;
}

const StrategyAnalysis: React.FC = () => {
  const [params, setParams] = useState<StrategyParams>({
    strategy_type: 'calendar_spread',
    expiration_days: 30,
    strike_percentage: 100,
    position_size: 1,
  });

  const analyzeStrategy = useMutation(async (strategyParams: StrategyParams) => {
    const response = await axios.post(`${API_BASE_URL}/strategy/analyze`, strategyParams);
    return response.data;
  });

  const handleParamChange = (param: keyof StrategyParams) => (
    event: React.ChangeEvent<HTMLInputElement | { value: unknown }>
  ) => {
    setParams({
      ...params,
      [param]: event.target.value,
    });
  };

  const handleAnalyze = () => {
    analyzeStrategy.mutate(params);
  };

  const strategyTypes = [
    { value: 'calendar_spread', label: 'Calendar Spread' },
    { value: 'butterfly', label: 'Iron Butterfly' },
    { value: 'straddle', label: 'Long Straddle' },
    { value: 'iron_condor', label: 'Iron Condor' },
    { value: 'backspread', label: 'Ratio Back Spread' },
  ];

  return (
    <Grid container spacing={3}>
      {/* Strategy Configuration */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Strategy Configuration
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
                label="Expiration Days"
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
                onClick={handleAnalyze}
                disabled={analyzeStrategy.isLoading}
                sx={{ mt: 2 }}
              >
                {analyzeStrategy.isLoading ? <CircularProgress size={24} /> : 'Analyze Strategy'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Analysis Results */}
      <Grid item xs={12} md={8}>
        {analyzeStrategy.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Error analyzing strategy. Please try again.
          </Alert>
        )}
        {analyzeStrategy.data && (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Risk Metrics
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Expected Profit
                      </Typography>
                      <Typography variant="h6">
                        ${analyzeStrategy.data.metrics.expected_profit.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Max Loss
                      </Typography>
                      <Typography variant="h6" color="error">
                        ${analyzeStrategy.data.metrics.max_loss.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Probability of Profit
                      </Typography>
                      <Typography variant="h6">
                        {(analyzeStrategy.data.metrics.probability_of_profit * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Sharpe Ratio
                      </Typography>
                      <Typography variant="h6">
                        {analyzeStrategy.data.metrics.risk_metrics.sharpe_ratio.toFixed(2)}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Greeks
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Delta
                      </Typography>
                      <Typography variant="h6">
                        {analyzeStrategy.data.metrics.greeks.delta.toFixed(3)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Gamma
                      </Typography>
                      <Typography variant="h6">
                        {analyzeStrategy.data.metrics.greeks.gamma.toFixed(3)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Theta
                      </Typography>
                      <Typography variant="h6">
                        {analyzeStrategy.data.metrics.greeks.theta.toFixed(3)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6} md={3}>
                      <Typography variant="body2" color="textSecondary">
                        Vega
                      </Typography>
                      <Typography variant="h6">
                        {analyzeStrategy.data.metrics.greeks.vega.toFixed(3)}
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

export default StrategyAnalysis; 