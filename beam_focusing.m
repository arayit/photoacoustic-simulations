    %% Mitutoyo Plan Apo (NA = 0.55)  |  λ = 1064 nm  |  Focus 3 mm deep in tissue
clear; clc; close all;

%% ── Parameters ───────────────────────────────────────────────────────────────
lambda = 1064e-6;   % Free-space wavelength [mm]
NA     = 0.55;      % Numerical aperture (in medium)
WD     = 3.0;       % Focal depth in medium [mm]
n      = 1.33;      % Refractive index (water / tissue)
d_air  = 2.0;       % Air gap: aperture to sample surface [mm]

%% ── Derived quantities ────────────────────────────────────────────────────────
theta_air = asin(NA);
theta_med = asin(NA / n);
w0        = lambda / (pi * NA);
zR        = pi * w0^2 * n / lambda;
R_surf    = w0 * sqrt(1 + (WD/zR)^2);
R_ap      = R_surf + d_air * tan(theta_air);
FWHM_r    = w0 * sqrt(2*log(2));
FWHM_z    = 2 * zR;

fprintf('\n  Mitutoyo Plan Apo | NA=%.2f | lambda=%.0fnm | n=%.2f\n', NA, lambda*1e6, n)
fprintf('  w0     = %.0f nm\n',   w0*1e6)
fprintf('  zR     = %.0f nm\n',   zR*1e6)
fprintf('  FWHM_r = %.0f nm\n',   FWHM_r*1e6)
fprintf('  FWHM_z = %.2f um\n\n', FWHM_z*1e3)

%% ── Magma-like colormap ───────────────────────────────────────────────────────
mag_pts = [0.00  0.000  0.000  0.000;
           0.20  0.110  0.020  0.280;
           0.40  0.440  0.055  0.490;
           0.60  0.820  0.190  0.260;
           0.78  0.970  0.520  0.085;
           0.92  0.995  0.855  0.440;
           1.00  1.000  0.995  0.900];
t_c      = linspace(0, 1, 256)';
magma_cmap = min(1, max(0, interp1(mag_pts(:,1), mag_pts(:,2:4), t_c)));

%% ── Figure ────────────────────────────────────────────────────────────────────
figure('Color','k', 'Position',[50 50 1300 900]);
tl = tiledlayout(2, 2, 'TileSpacing','compact', 'Padding','compact');
title(tl, ...
    sprintf('Mitutoyo Plan Apo  |  NA = %.2f  |  \\lambda = %.0f nm  |  n = %.2f  |  Focus %.1f mm deep', ...
    NA, lambda*1e6, n, WD), ...
    'FontSize',13, 'FontWeight','bold', 'Color',[0.88 0.88 0.88]);

%% ════════════════════════════════════════════════════════════════════════════
%%  Panel 1  –  Side view with magma intensity fill
%% ════════════════════════════════════════════════════════════════════════════
ax1 = nexttile(tl, [1 2]);
hold(ax1, 'on');

%── Gaussian intensity grid ───────────────────────────────────────────────────
Nz = 700;  Nr = 500;
z_sv = linspace(0, WD*1.08, Nz);
r_sv = linspace(-R_surf*1.10, R_surf*1.10, Nr);
[Zg_sv, Rg_sv] = meshgrid(z_sv, r_sv);

W_sv = w0 * sqrt(1 + ((z_sv - WD) / zR).^2);
W_sv_grid = repmat(W_sv, Nr, 1);
I_sv = exp(-2 * Rg_sv.^2 ./ W_sv_grid.^2);

imagesc(ax1, z_sv, r_sv, I_sv, [0 1]);
axis(ax1, 'xy');
axis(ax1, 'tight');
colormap(ax1, magma_cmap);

%── Optical axis ──────────────────────────────────────────────────────────────
plot(ax1, [z_sv(1) z_sv(end)], [0 0], '-', 'Color',[1 1 1 0.20], 'LineWidth',0.7);

%── Focal point ───────────────────────────────────────────────────────────────
plot(ax1, WD, 0, 'o', 'MarkerSize',6, ...
    'Color',[1 0.95 0.8], 'MarkerFaceColor',[1 0.95 0.8]);
text(ax1, WD + 0.05, -R_surf*0.08, sprintf('Focus\nz = %.0f mm', WD), ...
    'Color',[0.95 0.85 0.65], 'FontSize',9, 'VerticalAlignment','top');

%── Medium label ──────────────────────────────────────────────────────────────
text(ax1, WD*0.50, -R_surf*1.05, sprintf('n = %.2f  (water / tissue)', n), ...
    'Color',[0.55 0.55 0.65], 'FontSize',9, 'HorizontalAlignment','center');

set(ax1, 'Color','k', 'XColor',[0.7 0.7 0.7], 'YColor',[0.7 0.7 0.7], ...
    'GridColor',[0.25 0.25 0.25], 'FontSize',10, 'Box','off');
xlabel(ax1, 'z  (mm)', 'FontSize',11, 'Color',[0.8 0.8 0.8]);
ylabel(ax1, 'r  (mm)', 'FontSize',11, 'Color',[0.8 0.8 0.8]);
title(ax1, 'Side View — Beam Geometry', 'FontSize',12, 'FontWeight','bold', 'Color','w');
grid(ax1, 'off');

%% ════════════════════════════════════════════════════════════════════════════
%%  Panel 2  –  Focal-region I(r,z) cross-section  (µm scale)
%% ════════════════════════════════════════════════════════════════════════════
ax2 = nexttile(tl);
hold(ax2, 'on');

z_f = linspace(WD - 6e-3, WD + 6e-3, 500);
r_f = linspace(-3e-3, 3e-3, 500);
[Zg, Rg] = meshgrid(z_f, r_f);
Wz  = w0 * sqrt(1 + ((Zg - WD) ./ zR).^2);
Irz = (w0 ./ Wz).^2 .* exp(-2 * Rg.^2 ./ Wz.^2);

imagesc(ax2, (z_f - WD)*1e3, r_f*1e3, Irz);
axis(ax2, 'xy');
colormap(ax2, magma_cmap);
cb2 = colorbar(ax2);
cb2.Color = 'w';
cb2.Label.String  = 'I / I_0';
cb2.Label.Color   = 'w';
cb2.Label.FontSize = 10;

%── Beam envelope ─────────────────────────────────────────────────────────────
z_env = (z_f - WD)*1e3;
w_env = w0 * sqrt(1 + ((z_f - WD)./zR).^2) * 1e3;
h_env = plot(ax2,  z_env,  w_env, 'w--', 'LineWidth',1.2);
         plot(ax2,  z_env, -w_env, 'w--', 'LineWidth',1.2, 'HandleVisibility','off');

%── Legend ────────────────────────────────────────────────────────────────────
h_w0 = plot(ax2, NaN, NaN, 'LineStyle','none');
h_zR = plot(ax2, NaN, NaN, 'LineStyle','none');
legend(ax2, [h_env, h_w0, h_zR], ...
    {'$w(z) = w_0\sqrt{1+(z/z_R)^2}$', ...
     sprintf('$w_0 = \\lambda/(\\pi\\,\\mathrm{NA}) = %.0f\\,\\mathrm{nm}$', round(w0*1e6)), ...
     sprintf('$z_R = \\pi w_0^2 n/\\lambda = %.2f\\,\\mu\\mathrm{m}$', zR*1e3)}, ...
    'Interpreter','latex', 'TextColor','w', 'Color',[0.08 0.08 0.08], ...
    'EdgeColor',[0.30 0.30 0.30], 'FontSize',9, 'Location','northeast');

set(ax2, 'Color','k', 'XColor','w', 'YColor','w', 'FontSize',9, ...
    'XLim',[-6 6], 'YLim',[-3 3]);
xlabel(ax2, 'z - z_{foc}  (\mum)', 'FontSize',10, 'Color','w');
ylabel(ax2, 'r  (\mum)',            'FontSize',10, 'Color','w');
title(ax2, 'Focal Region  I(r,z)', 'FontSize',11, 'FontWeight','bold', 'Color','w');

%% ════════════════════════════════════════════════════════════════════════════
%%  Panel 3  –  Transverse 2-D map at focal plane
%% ════════════════════════════════════════════════════════════════════════════
ax3 = nexttile(tl);
hold(ax3, 'on');

r_xy  = linspace(-3.5*w0, 3.5*w0, 400);
[Xg3, Yg3] = meshgrid(r_xy, r_xy);
Rg_xy = sqrt(Xg3.^2 + Yg3.^2);
I_xy  = exp(-2 * Rg_xy.^2 / w0^2);

imagesc(ax3, r_xy*1e3, r_xy*1e3, I_xy, [0 1]);
axis(ax3, 'xy'); axis(ax3, 'equal'); axis(ax3, 'tight');
colormap(ax3, magma_cmap);
cb3 = colorbar(ax3);
cb3.Color = 'w';
cb3.Label.String  = 'I / I_0';
cb3.Label.Color   = 'w';
cb3.Label.FontSize = 10;

%── Annotation rings ──────────────────────────────────────────────────────────
theta_ring = linspace(0, 2*pi, 300);
r_half     = w0 * sqrt(log(2)/2);      % radius at I = 0.5 (→ FWHM = 2*r_half)

plot(ax3, w0    *cos(theta_ring)*1e3, w0    *sin(theta_ring)*1e3, ...
    'w--', 'LineWidth',1.5);
text(ax3, w0*cos(pi/4)*1e3 + 0.02, w0*sin(pi/4)*1e3, '1/e²', ...
    'Color','w', 'FontSize',9, 'HorizontalAlignment','left');

plot(ax3, r_half*cos(theta_ring)*1e3, r_half*sin(theta_ring)*1e3, ...
    '--', 'Color',[0.20 0.85 0.40], 'LineWidth',1.5);
text(ax3, r_half*cos(-pi/4)*1e3 + 0.02, r_half*sin(-pi/4)*1e3, 'FWHM', ...
    'Color',[0.20 0.85 0.40], 'FontSize',9, 'HorizontalAlignment','left');

%── Crosshairs ────────────────────────────────────────────────────────────────
plot(ax3, [r_xy(1) r_xy(end)]*1e3, [0 0], '-', 'Color',[1 1 1 0.18], 'LineWidth',0.7);
plot(ax3, [0 0], [r_xy(1) r_xy(end)]*1e3, '-', 'Color',[1 1 1 0.18], 'LineWidth',0.7);

set(ax3, 'Color','k', 'XColor','w', 'YColor','w', 'FontSize',9);
xlabel(ax3, 'x  (\mum)', 'FontSize',10, 'Color','w');
ylabel(ax3, 'y  (\mum)', 'FontSize',10, 'Color','w');
title(ax3, 'Focal Plane  I(x,y)', 'FontSize',11, 'FontWeight','bold', 'Color','w');

