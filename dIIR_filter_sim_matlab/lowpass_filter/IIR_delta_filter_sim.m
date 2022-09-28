clear
close all
clc

addpath('..\')

% Filter Specifications
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
OSR = 256;                          %oversample ratio
fb = 22050;                         %nyquist
fs = OSR*2*fb;                      %sampling frequency
ts = 1/fs;                          %sampling period
f = logspace(0,log10(fb),2^10);

% num_samples = 2^ceil(log2(1e6));
num_samples = 1e7;    %number of simulation samples
t_stop = ts*(num_samples-1);
t = 0:ts:t_stop;

% Filter Input Signal
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
amp = 0.5;
% fsig = 100*fs/num_samples;
% in = amp*sin(2*pi*fsig*t);
in = amp*(2*rand(1,length(t))-1); %white noise input

% Filter Design
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% lowpass filter
Rs = 60;
Wn = 2*pi*8000;
ftype = 'low';
% N = 6;
N = 4;
[A,B,C,D] = cheby2(N,Rs,Wn,ftype,'s');
[Ad,Bd,Cd,Dd] = c2delta(A,B,C,D,ts);

% %cheby2 bandpass filter
% Rs = 60;
% Wn = 2*pi.*[300 3000];
% ftype = 'bandpass';
% N = 4;
% [z,p,k] = cheby2(N/2,Rs,Wn,ftype,'s');
% [A,B,C,D] = zp2ss(z,p,k);
% [T, A] = balance(A);
% B = T\B;
% C = C*T;

% %convert to delta domain
% [Ad,Bd,Cd,Dd] = c2delta(A,B,C,D,ts);


% % cheby1 bandpass filter
% Rp = 0.1;
% Wn = 2*pi.*[100 500];
% ftype = 'bandpass';
% N = 6;
% [z,p,k] = cheby1(N/2,Rp,Wn,ftype,'s');
% [A,B,C,D] = zp2ss(z,p,k);
% % [T, A] = balance(A);
% % B = T\B;
% % C = C*T;
% [Ad,Bd,Cd,Dd] = c2delta(A,B,C,D,ts);

% %notch filter
% sigma = 100;
% fc = 2000;
% f = [1 10 logspace(log10(100),log10(fc-1),2^14)...
%     fc logspace(log10(fc+1),log10(fb),2^14)];
% N = 2;
% [A,B,C,D] = tf2ss([1 0 (2*pi*fc)^2],[1 sigma (2*pi*fc)^2]);
% [Ad,Bd,Cd,Dd] = c2delta(A,B,C,D,ts);

% Filter Implementation
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Structural transformation of filter
[Ad_t,Bd_t,Cd_t,Dd_t,T0] = obsv_cst(Ad,Bd,Cd,Dd);
[num_t, den_t] = ss2tf(Ad_t,Bd_t,Cd_t,Dd_t);

% Scaling
[Ts, k] = dIIR_scaling(Ad,Bd,T0,f,ts);
K_inv = diag(k);
Ad_ts = Ts\Ad_t*Ts;
Bd_ts = Ts\Bd_t;
Cd_ts = Cd_t*Ts;
Dd_ts = Dd_t;
num_ts = [num_t(1) num_t(2:end)./(diag(Ts)')];
den_ts = [1 den_t(2:end)./(diag(Ts)')];

beta = num_ts;
alpha = den_ts;
% bode(ss(A,B,C,D),tf(num_t,den_t));

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
disp(alpha);
disp(beta);
disp(k);

% Simulate Simulink Filter Model
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
sim_out = sim('filter_model');

filter_output = sim_out.filter_output.signals.values;
filter_state = sim_out.filter_state.signals.values;

disp(sim_out.filter_output.signals.dimensions)
disp(sim_out.filter_state.signals.dimensions)

% Plotting (Transfer Function Estimation)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

figure; hold on;
nx = max(size(filter_output));
na = 4;
w = hanning(floor(nx/na));

[H_mag, ~] = delta_bode(Ad,Bd,Cd,Dd,f,ts);
semilogx(f,20*log10(abs(squeeze(H_mag))),'linewidth',3);

[T_est1, ~] = tfestimate(in,filter_output,w,[],f,fs);
semilogx(f,20*log10(abs(T_est1)),'linewidth',3);

axis tight
title('Transfer Function Magnitude Estimation');
xlabel('Frequency (Hz)');
ylabel('Magnitude (dB)');
set(gca, 'XScale', 'log');
legend('Ideal Transfer Function',...
    'Ideal \delta Filter Simulation', 'location', 'best');

% Plotting (State Variables)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

figure;
[T_est2, ~] = tfestimate(in,filter_state,w,[],f,fs);
loglog(f,abs(T_est2)','linewidth',3);

axis tight
title('State Variable Bode Plot');
xlabel('Frequency (Hz)');
ylabel('Magnitude (dB)');
set(gca, 'XScale', 'log');


filter_output = []
filter_state = []
in = []
t = []
w = []
sim_out = []
save('all.mat')
