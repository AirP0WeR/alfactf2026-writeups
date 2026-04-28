package io.peakmood.mobile;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import io.peakmood.mobile.MiningSceneView;
import io.peakmood.mobile.TerrainModel;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.UUID;
import org.json.JSONObject;

/* JADX INFO: loaded from: classes.dex */
public class MainActivity extends Activity {
    private static final int DEFAULT_NODE_HP = 5;
    private static final long GEO_SYNC_MAX_INTERVAL_MS = 15000;
    private static final double GEO_SYNC_MIN_ALT_DELTA_M = 18.0d;
    private static final float GEO_SYNC_MIN_DISTANCE_M = 30.0f;
    private static final long GEO_SYNC_MIN_INTERVAL_MS = 4000;
    private static final int REQ_CAMERA = 43;
    private static final int REQ_LOCATION = 42;
    private static final long SESSION_RETRY_COOLDOWN_MS = 5000;
    private static final int SHARED_MAP_ZOOM_LEVEL = 19;
    private CameraPreviewView cameraPreviewView;
    private String currentNodeId;
    private String deviceId;
    private TextView encounterDetailsText;
    private TextView encounterLootText;
    private WorldMapView encounterMapView;
    private View encounterScreen;
    private TextView encounterStatusText;
    private Location lastGeoSyncLocation;
    private Button leaveEncounterButton;
    private Location liveLocation;
    private LocationManager locationManager;
    private MiningSceneView miningSceneView;
    private ProgressBar nodeProgress;
    private TextView nodeTitleText;
    private Button resumeEncounterButton;
    private TextView roamCoordsText;
    private TextView roamDetailsText;
    private TextView roamLootText;
    private TextView roamMapMetaText;
    private WorldMapView roamMapView;
    private View roamScreen;
    private TextView roamStatusText;
    private String sessionToken;
    private TerrainModel terrainModel;
    private String currentTier = "none";
    private int currentNodeHp = 0;
    private int currentHitsLeft = 0;
    private double currentNodeLat = Double.NaN;
    private double currentNodeLon = Double.NaN;
    private double lastLat = 0.0d;
    private double lastLon = 0.0d;
    private double lastAlt = 0.0d;
    private boolean hasLastLocation = false;
    private boolean encounterVisible = false;
    private boolean sessionInFlight = false;
    private boolean scanInFlight = false;
    private boolean hitInFlight = false;
    private boolean openInFlight = false;
    private boolean connectionDialogVisible = false;
    private long lastSessionAttemptAtMs = 0;
    private long lastGeoSyncAtMs = 0;
    private final LocationListener liveLocationListener = new LocationListener() { // from class: io.peakmood.mobile.MainActivity.1
        @Override // android.location.LocationListener
        public void onLocationChanged(Location location) {
            MainActivity.this.applyLiveLocation(location);
        }

        @Override // android.location.LocationListener
        public void onStatusChanged(String str, int i, Bundle bundle) {
        }

        @Override // android.location.LocationListener
        public void onProviderEnabled(String str) {
        }

        @Override // android.location.LocationListener
        public void onProviderDisabled(String str) {
        }
    };

    @Override // android.app.Activity
    protected void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        setContentView(R.layout.activity_main);
        this.locationManager = (LocationManager) getSystemService("location");
        this.deviceId = loadOrCreateDeviceId();
        this.terrainModel = TerrainModel.getInstance(this);
        bindViews();
        configureMapViews();
        configureButtons();
        resetNodeUi();
        setLootText(getString(R.string.loot_empty));
        showRoamMode();
        ensureLocationBootstrap();
        ensureCameraPermission();
    }

    @Override // android.app.Activity
    protected void onResume() {
        super.onResume();
        updateCameraPreview();
        startLiveLocationUpdates();
        ensureLocationBootstrap();
    }

    @Override // android.app.Activity
    protected void onPause() {
        stopLiveLocationUpdates();
        this.cameraPreviewView.stopPreview();
        super.onPause();
    }

    private void bindViews() {
        this.roamScreen = findViewById(R.id.roamScreen);
        this.encounterScreen = findViewById(R.id.encounterScreen);
        this.roamStatusText = (TextView) findViewById(R.id.roamStatusText);
        this.roamCoordsText = (TextView) findViewById(R.id.roamCoordsText);
        this.roamDetailsText = (TextView) findViewById(R.id.roamDetailsText);
        this.roamLootText = (TextView) findViewById(R.id.roamLootText);
        this.roamMapMetaText = (TextView) findViewById(R.id.roamMapMetaText);
        this.encounterStatusText = (TextView) findViewById(R.id.encounterStatusText);
        this.encounterDetailsText = (TextView) findViewById(R.id.encounterDetailsText);
        this.encounterLootText = (TextView) findViewById(R.id.encounterLootText);
        this.nodeTitleText = (TextView) findViewById(R.id.nodeTitleText);
        this.nodeProgress = (ProgressBar) findViewById(R.id.nodeProgress);
        this.resumeEncounterButton = (Button) findViewById(R.id.resumeEncounterButton);
        this.leaveEncounterButton = (Button) findViewById(R.id.leaveEncounterButton);
        this.cameraPreviewView = (CameraPreviewView) findViewById(R.id.cameraPreviewView);
        this.miningSceneView = (MiningSceneView) findViewById(R.id.miningSceneView);
        this.roamMapView = (WorldMapView) findViewById(R.id.roamMapView);
        this.encounterMapView = (WorldMapView) findViewById(R.id.encounterMapView);
    }

    private void configureButtons() {
        this.resumeEncounterButton.setOnClickListener(new View.OnClickListener() { // from class: io.peakmood.mobile.MainActivity.2
            @Override // android.view.View.OnClickListener
            public void onClick(View view) {
                if (MainActivity.this.currentNodeId != null) {
                    MainActivity.this.showEncounterMode();
                }
            }
        });
        this.leaveEncounterButton.setOnClickListener(new View.OnClickListener() { // from class: io.peakmood.mobile.MainActivity.3
            @Override // android.view.View.OnClickListener
            public void onClick(View view) {
                MainActivity.this.showRoamMode();
            }
        });
        this.miningSceneView.setOnNodeTapListener(new MiningSceneView.OnNodeTapListener() { // from class: io.peakmood.mobile.MainActivity.4
            @Override // io.peakmood.mobile.MiningSceneView.OnNodeTapListener
            public void onNodeTap() {
                MainActivity.this.handleMiningTap();
            }
        });
    }

    private void configureMapViews() {
        this.roamMapView.setViewportMode(1);
        this.encounterMapView.setViewportMode(1);
        this.roamMapView.setZoomLevelOverride(SHARED_MAP_ZOOM_LEVEL);
        this.encounterMapView.setZoomLevelOverride(SHARED_MAP_ZOOM_LEVEL);
    }

    private String loadOrCreateDeviceId() {
        SharedPreferences sharedPreferences = getSharedPreferences("peakmood", 0);
        String string = sharedPreferences.getString("device_id", null);
        if (string != null) {
            return string;
        }
        String string2 = UUID.randomUUID().toString();
        sharedPreferences.edit().putString("device_id", string2).apply();
        return string2;
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void showRoamMode() {
        this.encounterVisible = false;
        this.roamScreen.setVisibility(0);
        this.encounterScreen.setVisibility(8);
        updateCameraPreview();
        updateResumeEncounterButton();
        refreshActionButtons();
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void showEncounterMode() {
        this.encounterVisible = true;
        this.roamScreen.setVisibility(8);
        this.encounterScreen.setVisibility(0);
        updateCameraPreview();
        updateResumeEncounterButton();
        refreshActionButtons();
    }

    private void updateResumeEncounterButton() {
        this.resumeEncounterButton.setVisibility(this.currentNodeId == null ? 8 : 0);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void refreshActionButtons() {
        this.resumeEncounterButton.setEnabled((this.currentNodeId == null || this.openInFlight) ? false : true);
        this.leaveEncounterButton.setEnabled((this.hitInFlight || this.openInFlight) ? false : true);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void setLootText(String str) {
        this.roamLootText.setText(str);
        this.encounterLootText.setText(str);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void setSharedStatus(String str, String str2, String str3) {
        this.roamStatusText.setText(str);
        this.roamDetailsText.setText(str2);
        this.roamMapMetaText.setText(str3);
        this.encounterStatusText.setText(str);
        this.encounterDetailsText.setText(str2);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void resetNodeUi() {
        this.currentNodeId = null;
        this.currentTier = "none";
        this.currentNodeHp = 0;
        this.currentHitsLeft = 0;
        this.currentNodeLat = Double.NaN;
        this.currentNodeLon = Double.NaN;
        this.nodeProgress.setMax(DEFAULT_NODE_HP);
        this.nodeProgress.setProgress(0);
        this.nodeTitleText.setText(R.string.node_idle);
        this.nodeTitleText.setVisibility(8);
        this.miningSceneView.clearNode();
        updateResumeEncounterButton();
        refreshActionButtons();
        pushMapState();
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void updateMiningScene() {
        this.miningSceneView.setNodeState(this.currentNodeId != null, this.currentTier, this.currentHitsLeft, this.currentNodeHp);
        this.nodeTitleText.setVisibility(this.currentNodeId == null ? 8 : 0);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void handleMiningTap() {
        if (this.currentNodeId == null || this.hitInFlight || this.openInFlight || this.sessionInFlight || this.miningSceneView.isImpactAnimationRunning()) {
            return;
        }
        if (this.currentHitsLeft > 0) {
            if (!this.miningSceneView.triggerImpact()) {
                return;
            }
            hitNode();
            return;
        }
        openNode();
    }

    private void ensureCameraPermission() {
        if (hasCameraPermission()) {
            updateCameraPreview();
        } else {
            requestPermissions(new String[]{"android.permission.CAMERA"}, REQ_CAMERA);
        }
    }

    private void updateCameraPreview() {
        if (this.encounterVisible && hasCameraPermission()) {
            this.cameraPreviewView.startPreview();
        } else {
            this.cameraPreviewView.stopPreview();
        }
    }

    private boolean hasCameraPermission() {
        return checkSelfPermission("android.permission.CAMERA") == 0;
    }

    private void ensureLocationBootstrap() {
        if (!hasLocationPermission()) {
            requestPermissions(new String[]{"android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"}, REQ_LOCATION);
        } else {
            startLiveLocationUpdates();
            ensureSessionConnected(false);
        }
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void ensureSessionConnected(boolean z) {
        if (this.sessionToken != null || this.sessionInFlight) {
            return;
        }
        long jCurrentTimeMillis = System.currentTimeMillis();
        if (!z && (this.connectionDialogVisible || jCurrentTimeMillis - this.lastSessionAttemptAtMs < SESSION_RETRY_COOLDOWN_MS)) {
            return;
        }
        this.lastSessionAttemptAtMs = jCurrentTimeMillis;
        openSession();
    }

    private void openSession() {
        if (this.sessionInFlight) {
            return;
        }
        this.sessionInFlight = true;
        refreshActionButtons();
        setSharedStatus("Подключаю профиль…", "Сверяю карту, обзор и ближайшие сигналы.", "СВЯЗЬ");
        new Thread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.5
            @Override // java.lang.Runnable
            public void run() {
                try {
                    JSONObject jSONObject = new JSONObject();
                    jSONObject.put("device_id", MainActivity.this.deviceId);
                    jSONObject.put("client_version", "1.0.0");
                    jSONObject.put("model", Build.MODEL);
                    JSONObject jSONObjectPostJson = MainActivity.this.postJson("/api/v1/session/open", jSONObject, null);
                    MainActivity.this.sessionToken = jSONObjectPostJson.getString("session_token");
                    MainActivity.this.runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.5.1
                        @Override // java.lang.Runnable
                        public void run() {
                            MainActivity.this.sessionInFlight = false;
                            MainActivity.this.refreshActionButtons();
                            MainActivity.this.setSharedStatus("Полевой режим готов", "Карта активна. Находки будут появляться автоматически по мере движения.", "В СЕТИ");
                            if (MainActivity.this.liveLocation != null) {
                                MainActivity.this.triggerGeoSync(new Location(MainActivity.this.liveLocation), true);
                            }
                        }
                    });
                } catch (Exception e) {
                    MainActivity.this.showConnectionFailure();
                }
            }
        }).start();
    }

    private boolean hasLocationPermission() {
        return checkSelfPermission("android.permission.ACCESS_FINE_LOCATION") == 0 || checkSelfPermission("android.permission.ACCESS_COARSE_LOCATION") == 0;
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void triggerGeoSync(Location location, boolean z) {
        if (location == null) {
            return;
        }
        if (this.sessionToken == null) {
            ensureSessionConnected(z);
            return;
        }
        if (this.currentNodeId != null || this.hitInFlight || this.openInFlight || this.scanInFlight || this.sessionInFlight) {
            return;
        }
        long jCurrentTimeMillis = System.currentTimeMillis();
        if (!z) {
            if (this.lastGeoSyncLocation != null) {
                boolean z2 = location.distanceTo(this.lastGeoSyncLocation) >= GEO_SYNC_MIN_DISTANCE_M || Math.abs(Math.abs(readAltitude(location)) - Math.abs(readAltitude(this.lastGeoSyncLocation))) >= GEO_SYNC_MIN_ALT_DELTA_M;
                boolean z3 = jCurrentTimeMillis - this.lastGeoSyncAtMs >= GEO_SYNC_MAX_INTERVAL_MS;
                if (!z2 && !z3) {
                    return;
                }
            }
            if (jCurrentTimeMillis - this.lastGeoSyncAtMs < GEO_SYNC_MIN_INTERVAL_MS) {
                return;
            }
        }
        submitScan(new Location(location));
    }

    private Location bestLastKnownLocation() {
        long jCurrentTimeMillis = System.currentTimeMillis();
        String[] strArr = {"gps", "network", "passive"};
        Location location = null;
        for (int i = 0; i < 3; i++) {
            try {
                Location lastKnownLocation = this.locationManager.getLastKnownLocation(strArr[i]);
                if (lastKnownLocation != null && jCurrentTimeMillis - lastKnownLocation.getTime() <= GEO_SYNC_MAX_INTERVAL_MS && (location == null || lastKnownLocation.getTime() > location.getTime())) {
                    location = lastKnownLocation;
                }
            } catch (SecurityException e) {
                return null;
            }
        }
        return location;
    }

    private void submitScan(final Location location) {
        this.scanInFlight = true;
        this.lastGeoSyncAtMs = System.currentTimeMillis();
        this.lastGeoSyncLocation = new Location(location);
        refreshActionButtons();
        captureLocation(location);
        this.roamCoordsText.setText(formatLocationSummary(location));
        setSharedStatus("Синхронизирую сектор…", "Сверяю позицию и обновляю ближайшие сигналы вокруг тебя.", "ПОИСК");
        new Thread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.6
            @Override // java.lang.Runnable
            public void run() {
                try {
                    JSONObject jSONObject = new JSONObject();
                    jSONObject.put("lat", location.getLatitude());
                    jSONObject.put("lon", location.getLongitude());
                    jSONObject.put("reported_alt_m", location.hasAltitude() ? location.getAltitude() : 0.0d);
                    jSONObject.put("vertical_accuracy_m", location.hasVerticalAccuracy() ? location.getVerticalAccuracyMeters() : 0.0d);
                    final JSONObject jSONObjectPostJson = MainActivity.this.postJson("/api/v1/geo/update", jSONObject, MainActivity.this.sessionToken);
                    final int iOptInt = jSONObjectPostJson.optInt("_http_status", 200);
                    MainActivity.this.runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.6.1
                        @Override // java.lang.Runnable
                        public void run() {
                            MainActivity.this.handleScanResponse(iOptInt, jSONObjectPostJson);
                        }
                    });
                } catch (Exception e) {
                    MainActivity.this.showError(MainActivity.this.getString(R.string.service_unavailable));
                }
            }
        }).start();
    }

    private void startLiveLocationUpdates() {
        if (!hasLocationPermission()) {
            return;
        }
        stopLiveLocationUpdates();
        String[] strArr = {"gps", "network", "passive"};
        for (int i = 0; i < 3; i++) {
            String str = strArr[i];
            try {
                if (this.locationManager.isProviderEnabled(str)) {
                    this.locationManager.requestLocationUpdates(str, 1000L, 0.0f, this.liveLocationListener, Looper.getMainLooper());
                }
            } catch (IllegalArgumentException e) {
            } catch (SecurityException e2) {
                return;
            }
        }
        Location locationBestLastKnownLocation = bestLastKnownLocation();
        if (locationBestLastKnownLocation != null) {
            applyLiveLocation(locationBestLastKnownLocation);
        }
    }

    private void stopLiveLocationUpdates() {
        try {
            this.locationManager.removeUpdates(this.liveLocationListener);
        } catch (SecurityException e) {
        }
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void applyLiveLocation(Location location) {
        this.liveLocation = new Location(location);
        captureLocation(this.liveLocation);
        if (isCurrentNodeStaleFor(this.liveLocation)) {
            resetNodeUi();
            setSharedStatus("Сектор обновлён", formatTerrainDetails(readAltitude(this.liveLocation)), "ПОИСК");
        }
        if (this.currentNodeId == null) {
            this.roamCoordsText.setText(formatLocationSummary(this.liveLocation));
        }
        if (this.sessionToken == null) {
            ensureSessionConnected(false);
        } else {
            if (this.currentNodeId != null) {
                return;
            }
            triggerGeoSync(new Location(this.liveLocation), false);
        }
    }

    private void captureLocation(Location location) {
        this.hasLastLocation = true;
        this.lastLat = location.getLatitude();
        this.lastLon = location.getLongitude();
        this.lastAlt = location.hasAltitude() ? location.getAltitude() : 0.0d;
        pushMapState();
    }

    private boolean isCurrentNodeStaleFor(Location location) {
        if (this.currentNodeId == null || location == null) {
            return false;
        }
        return !this.currentTier.equals(tierForAltitude(readAltitude(location)));
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void handleScanResponse(int i, JSONObject jSONObject) {
        String str;
        this.scanInFlight = false;
        if (i >= 400) {
            resetNodeUi();
            setSharedStatus("Сигнал не прошёл проверку", this.hasLastLocation ? formatTerrainDetails(this.lastAlt) : "Высота пока не подтверждена. Повтори скан через несколько секунд.", "ПРОВЕРКА");
            setLootText("В этом секторе пока нет подтверждённой находки.");
            showRoamMode();
            return;
        }
        JSONObject jSONObjectOptJSONObject = jSONObject.optJSONObject("scan");
        if (jSONObjectOptJSONObject == null) {
            showError("Пустой ответ сервера.");
            return;
        }
        String strOptString = jSONObjectOptJSONObject.optString("tier", "none");
        String strOptString2 = jSONObjectOptJSONObject.optString("display_name", "Скан завершён");
        double dOptDouble = jSONObjectOptJSONObject.optDouble("reported_alt_m", this.lastAlt);
        String terrainDetails = formatTerrainDetails(dOptDouble);
        if ("none".equals(strOptString)) {
            str = "ПОИСК";
        } else {
            str = String.format(Locale.US, "%s · %.0f м", tierLabelUpper(strOptString), Double.valueOf(dOptDouble));
        }
        setSharedStatus(strOptString2, terrainDetails, str);
        JSONObject jSONObjectOptJSONObject2 = jSONObjectOptJSONObject.optJSONObject("node");
        if (jSONObjectOptJSONObject2 == null) {
            resetNodeUi();
            setLootText(jSONObjectOptJSONObject.optString("message", "Нода не найдена."));
            showRoamMode();
            return;
        }
        this.currentTier = strOptString;
        this.currentNodeId = jSONObjectOptJSONObject2.optString("id", null);
        this.currentNodeHp = jSONObjectOptJSONObject2.optInt("hp_total", 1);
        this.currentHitsLeft = jSONObjectOptJSONObject2.optInt("hits_left", this.currentNodeHp);
        this.currentNodeLat = jSONObjectOptJSONObject2.optDouble("lat", Double.NaN);
        this.currentNodeLon = jSONObjectOptJSONObject2.optDouble("lon", Double.NaN);
        this.nodeProgress.setMax(this.currentNodeHp);
        this.nodeProgress.setProgress(this.currentNodeHp - this.currentHitsLeft);
        this.nodeTitleText.setText(jSONObjectOptJSONObject2.optString("display_name", "Жеода"));
        updateMiningScene();
        refreshActionButtons();
        pushMapState();
        showRoamMode();
    }

    private void hitNode() {
        if (this.currentNodeId == null || this.hitInFlight || this.openInFlight) {
            return;
        }
        this.hitInFlight = true;
        refreshActionButtons();
        new Thread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.7
            @Override // java.lang.Runnable
            public void run() {
                try {
                    JSONObject jSONObject = new JSONObject();
                    jSONObject.put("node_id", MainActivity.this.currentNodeId);
                    JSONObject jSONObjectPostJson = MainActivity.this.postJson("/api/v1/node/hit", jSONObject, MainActivity.this.sessionToken);
                    final int iOptInt = jSONObjectPostJson.optInt("_http_status", 200);
                    if (iOptInt >= 400) {
                        final String strOptString = jSONObjectPostJson.optString("error", MainActivity.this.getString(R.string.service_unavailable));
                        MainActivity.this.runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.7.1
                            @Override // java.lang.Runnable
                            public void run() {
                                MainActivity.this.hitInFlight = false;
                                if (iOptInt == 401 || iOptInt == 404) {
                                    MainActivity.this.resetNodeUi();
                                    MainActivity.this.showRoamMode();
                                }
                                MainActivity.this.setSharedStatus("Сигнал сброшен", strOptString, "СБОЙ");
                                MainActivity.this.refreshActionButtons();
                            }
                        });
                    } else {
                        final JSONObject jSONObject2 = jSONObjectPostJson.getJSONObject("node");
                        MainActivity.this.runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.7.2
                            @Override // java.lang.Runnable
                            public void run() {
                                MainActivity.this.hitInFlight = false;
                                MainActivity.this.currentHitsLeft = jSONObject2.optInt("hits_left", MainActivity.this.currentHitsLeft);
                                MainActivity.this.nodeProgress.setProgress(MainActivity.this.currentNodeHp - MainActivity.this.currentHitsLeft);
                                MainActivity.this.updateMiningScene();
                                MainActivity.this.pushMapState();
                                if (MainActivity.this.currentHitsLeft == 0) {
                                    MainActivity.this.setSharedStatus("Жеода раскрыта", "Внутренний слой открыт. Тапни по жеоде ещё раз, чтобы забрать образец.", "ГОТОВО");
                                } else {
                                    MainActivity.this.setSharedStatus("Минерал поддаётся", String.format(Locale.US, "Осталось ударов: %d. Продолжай бить по жеоде.", Integer.valueOf(MainActivity.this.currentHitsLeft)), String.format(Locale.US, "УДАР %d/%d", Integer.valueOf(MainActivity.this.currentNodeHp - MainActivity.this.currentHitsLeft), Integer.valueOf(MainActivity.this.currentNodeHp)));
                                }
                                MainActivity.this.refreshActionButtons();
                            }
                        });
                    }
                } catch (Exception e) {
                    MainActivity.this.showError(MainActivity.this.getString(R.string.service_unavailable));
                }
            }
        }).start();
    }

    private void openNode() {
        if (this.currentNodeId == null || this.hitInFlight || this.openInFlight) {
            return;
        }
        this.openInFlight = true;
        refreshActionButtons();
        new Thread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.8
            @Override // java.lang.Runnable
            public void run() {
                try {
                    JSONObject jSONObject = new JSONObject();
                    jSONObject.put("node_id", MainActivity.this.currentNodeId);
                    JSONObject jSONObjectPostJson = MainActivity.this.postJson("/api/v1/node/open", jSONObject, MainActivity.this.sessionToken);
                    final int iOptInt = jSONObjectPostJson.optInt("_http_status", 200);
                    if (iOptInt >= 400) {
                        final String strOptString = jSONObjectPostJson.optString("error", MainActivity.this.getString(R.string.service_unavailable));
                        MainActivity.this.runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.8.1
                            @Override // java.lang.Runnable
                            public void run() {
                                MainActivity.this.openInFlight = false;
                                if (iOptInt == 401 || iOptInt == 404) {
                                    MainActivity.this.resetNodeUi();
                                    MainActivity.this.showRoamMode();
                                }
                                MainActivity.this.setSharedStatus("Жеода недоступна", strOptString, "СБОЙ");
                                MainActivity.this.refreshActionButtons();
                            }
                        });
                    } else {
                        final JSONObject jSONObject2 = jSONObjectPostJson.getJSONObject("loot");
                        MainActivity.this.runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.8.2
                            @Override // java.lang.Runnable
                            public void run() {
                                MainActivity.this.openInFlight = false;
                                MainActivity.this.setSharedStatus(jSONObject2.optString("display_name", "Добыча получена"), jSONObject2.optString("flavor", ""), "ДОБЫТО");
                                StringBuilder sb = new StringBuilder();
                                sb.append("Редкость: ").append(MainActivity.this.tierLabel(jSONObject2.optString("tier", "unknown")));
                                if (jSONObject2.has("artifact_signature")) {
                                    sb.append("\n\n").append(MainActivity.this.getString(R.string.loot_signature_label)).append(": ").append(jSONObject2.optString("artifact_signature", ""));
                                }
                                MainActivity.this.setLootText(sb.toString());
                                MainActivity.this.resetNodeUi();
                                MainActivity.this.showRoamMode();
                            }
                        });
                    }
                } catch (Exception e) {
                    MainActivity.this.showError(MainActivity.this.getString(R.string.service_unavailable));
                }
            }
        }).start();
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void pushMapState() {
        updateMiningScene();
        if (this.hasLastLocation) {
            this.roamMapView.setPlayerLocation(this.lastLat, this.lastLon, this.lastAlt);
            this.encounterMapView.setPlayerLocation(this.lastLat, this.lastLon, this.lastAlt);
        }
        boolean z = this.currentNodeId != null;
        this.roamMapView.setNodeState(z, this.currentNodeId, this.currentTier, this.currentHitsLeft, this.currentNodeHp, this.currentNodeLat, this.currentNodeLon);
        this.encounterMapView.setNodeState(z, this.currentNodeId, this.currentTier, this.currentHitsLeft, this.currentNodeHp, this.currentNodeLat, this.currentNodeLon);
    }

    /* JADX INFO: Access modifiers changed from: private */
    public JSONObject postJson(String str, JSONObject jSONObject, String str2) throws Exception {
        HttpURLConnection httpURLConnection = (HttpURLConnection) new URL(getString(R.string.base_url) + str).openConnection();
        httpURLConnection.setRequestMethod("POST");
        httpURLConnection.setConnectTimeout(6000);
        httpURLConnection.setReadTimeout(6000);
        httpURLConnection.setDoOutput(true);
        httpURLConnection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        if (str2 != null) {
            httpURLConnection.setRequestProperty("Authorization", "Bearer " + str2);
        }
        byte[] bytes = jSONObject.toString().getBytes(StandardCharsets.UTF_8);
        OutputStream outputStream = httpURLConnection.getOutputStream();
        try {
            outputStream.write(bytes);
            if (outputStream != null) {
                outputStream.close();
            }
            int responseCode = httpURLConnection.getResponseCode();
            String fully = readFully(responseCode >= 400 ? httpURLConnection.getErrorStream() : httpURLConnection.getInputStream());
            JSONObject jSONObject2 = fully.isEmpty() ? new JSONObject() : new JSONObject(fully);
            jSONObject2.put("_http_status", responseCode);
            httpURLConnection.disconnect();
            return jSONObject2;
        } catch (Throwable th) {
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (Throwable th2) {
                    Throwable.class.getDeclaredMethod("addSuppressed", Throwable.class).invoke(th, th2);
                }
            }
            throw th;
        }
    }

    private String readFully(InputStream inputStream) throws Exception {
        if (inputStream == null) {
            return "";
        }
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream, StandardCharsets.UTF_8));
        try {
            StringBuilder sb = new StringBuilder();
            while (true) {
                String line = bufferedReader.readLine();
                if (line != null) {
                    sb.append(line);
                } else {
                    String string = sb.toString();
                    bufferedReader.close();
                    return string;
                }
            }
        } catch (Throwable th) {
            try {
                bufferedReader.close();
            } catch (Throwable th2) {
                Throwable.class.getDeclaredMethod("addSuppressed", Throwable.class).invoke(th, th2);
            }
            throw th;
        }
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void showError(final String str) {
        runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.9
            @Override // java.lang.Runnable
            public void run() {
                MainActivity.this.scanInFlight = false;
                MainActivity.this.hitInFlight = false;
                MainActivity.this.openInFlight = false;
                MainActivity.this.refreshActionButtons();
                MainActivity.this.setSharedStatus("Сервис недоступен", str, "НЕТ СВЯЗИ");
            }
        });
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void showConnectionFailure() {
        runOnUiThread(new Runnable() { // from class: io.peakmood.mobile.MainActivity.10
            @Override // java.lang.Runnable
            public void run() {
                MainActivity.this.sessionInFlight = false;
                MainActivity.this.sessionToken = null;
                MainActivity.this.refreshActionButtons();
                MainActivity.this.setSharedStatus("Сервис недоступен", MainActivity.this.getString(R.string.service_unavailable), "НЕТ СВЯЗИ");
                MainActivity.this.showReconnectDialog();
            }
        });
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void showReconnectDialog() {
        if (this.connectionDialogVisible || isFinishing() || isDestroyed()) {
            return;
        }
        this.connectionDialogVisible = true;
        AlertDialog alertDialogCreate = new AlertDialog.Builder(this).setTitle(R.string.connection_alert_title).setMessage(R.string.connection_alert_message).setCancelable(true).setPositiveButton(R.string.connection_retry, new DialogInterface.OnClickListener() { // from class: io.peakmood.mobile.MainActivity.12
            @Override // android.content.DialogInterface.OnClickListener
            public void onClick(DialogInterface dialogInterface, int i) {
                MainActivity.this.connectionDialogVisible = false;
                MainActivity.this.ensureSessionConnected(true);
            }
        }).setNegativeButton(R.string.connection_retry_later, new DialogInterface.OnClickListener() { // from class: io.peakmood.mobile.MainActivity.11
            @Override // android.content.DialogInterface.OnClickListener
            public void onClick(DialogInterface dialogInterface, int i) {
                MainActivity.this.connectionDialogVisible = false;
            }
        }).create();
        alertDialogCreate.setOnDismissListener(new DialogInterface.OnDismissListener() { // from class: io.peakmood.mobile.MainActivity.13
            @Override // android.content.DialogInterface.OnDismissListener
            public void onDismiss(DialogInterface dialogInterface) {
                MainActivity.this.connectionDialogVisible = false;
            }
        });
        alertDialogCreate.show();
    }

    private double readAltitude(Location location) {
        if (location.hasAltitude()) {
            return location.getAltitude();
        }
        return 0.0d;
    }

    private TerrainModel.TerrainSnapshot terrainSnapshotFor(Location location) {
        if (location == null) {
            return null;
        }
        return terrainSnapshotFor(location.getLatitude(), location.getLongitude(), readAltitude(location));
    }

    private TerrainModel.TerrainSnapshot terrainSnapshotFor(double d, double d2, double d3) {
        if (this.terrainModel == null) {
            return null;
        }
        return this.terrainModel.snapshot(d, d2, d3);
    }

    private String formatTerrainDetails(double d) {
        TerrainModel.TerrainSnapshot terrainSnapshotTerrainSnapshotFor;
        if (this.hasLastLocation && (terrainSnapshotTerrainSnapshotFor = terrainSnapshotFor(this.lastLat, this.lastLon, d)) != null) {
            Locale locale = Locale.US;
            String str = terrainSnapshotTerrainSnapshotFor.label;
            String signedMeters = formatSignedMeters(d);
            String signedMeters2 = formatSignedMeters(terrainSnapshotTerrainSnapshotFor.expectedElevationM);
            double dAbs = Math.abs(terrainSnapshotTerrainSnapshotFor.expectedElevationM);
            double dAbs2 = Math.abs(d);
            Double.isNaN(dAbs);
            return String.format(locale, "%s · GPS %s · карта %s · Δmod %.0f м", str, signedMeters, signedMeters2, Double.valueOf(Math.abs(dAbs - dAbs2)));
        }
        return String.format(Locale.US, "GPS %s", formatSignedMeters(d));
    }

    private String formatSignedMeters(double d) {
        return String.format(Locale.US, "%+.0f м", Double.valueOf(d));
    }

    /* JADX INFO: Access modifiers changed from: private */
    public String tierLabel(String str) {
        if ("common".equals(str)) {
            return "обычный";
        }
        if ("rare".equals(str)) {
            return "редкий";
        }
        if ("epic".equals(str)) {
            return "эпический";
        }
        if ("FLAG".equals(str)) {
            return "мифический";
        }
        return "Сканируем...";
    }

    private String tierLabelUpper(String str) {
        return tierLabel(str).toUpperCase(new Locale("ru"));
    }

    private String tierForAltitude(double d) {
        if (d >= 9500.0d) {
            return "FLAG";
        }
        if (d >= 4200.0d) {
            return "epic";
        }
        if (d >= 1800.0d) {
            return "rare";
        }
        return "common";
    }

    private String formatLocationSummary(Location location) {
        double latitude = location.getLatitude();
        double longitude = location.getLongitude();
        double altitude = location.hasAltitude() ? location.getAltitude() : 0.0d;
        TerrainModel.TerrainSnapshot terrainSnapshotTerrainSnapshotFor = terrainSnapshotFor(location);
        if (terrainSnapshotTerrainSnapshotFor == null) {
            return String.format(Locale.US, "%s %.4f · %s %.4f · %.0f м", latitude < 0.0d ? "Ю" : "С", Double.valueOf(Math.abs(latitude)), longitude < 0.0d ? "З" : "В", Double.valueOf(Math.abs(longitude)), Double.valueOf(altitude));
        }
        Locale locale = Locale.US;
        String str = latitude < 0.0d ? "Ю" : "С";
        Double dValueOf = Double.valueOf(Math.abs(latitude));
        String str2 = longitude < 0.0d ? "З" : "В";
        Double dValueOf2 = Double.valueOf(Math.abs(longitude));
        String signedMeters = formatSignedMeters(altitude);
        String signedMeters2 = formatSignedMeters(terrainSnapshotTerrainSnapshotFor.expectedElevationM);
        double dAbs = Math.abs(terrainSnapshotTerrainSnapshotFor.expectedElevationM);
        double dAbs2 = Math.abs(altitude);
        Double.isNaN(dAbs);
        return String.format(locale, "%s %.4f · %s %.4f\nGPS %s · карта %s · Δmod %.0f м", str, dValueOf, str2, dValueOf2, signedMeters, signedMeters2, Double.valueOf(Math.abs(dAbs - dAbs2)));
    }

    @Override // android.app.Activity
    public void onRequestPermissionsResult(int i, String[] strArr, int[] iArr) {
        super.onRequestPermissionsResult(i, strArr, iArr);
        boolean z = true;
        if (i == REQ_LOCATION) {
            int length = iArr.length;
            int i2 = 0;
            while (true) {
                if (i2 >= length) {
                    z = false;
                    break;
                } else if (iArr[i2] == 0) {
                    break;
                } else {
                    i2++;
                }
            }
            if (z) {
                ensureLocationBootstrap();
                return;
            } else {
                showError(getString(R.string.permission_needed));
                return;
            }
        }
        if (i == REQ_CAMERA) {
            int length2 = iArr.length;
            int i3 = 0;
            while (true) {
                if (i3 >= length2) {
                    z = false;
                    break;
                } else if (iArr[i3] == 0) {
                    break;
                } else {
                    i3++;
                }
            }
            if (z) {
                updateCameraPreview();
            } else {
                showError(getString(R.string.camera_permission_needed));
                setLootText(getString(R.string.camera_unavailable));
            }
        }
    }
}
