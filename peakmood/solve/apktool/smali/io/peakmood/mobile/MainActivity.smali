.class public Lio/peakmood/mobile/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"


# static fields
.field private static final DEFAULT_NODE_HP:I = 0x5

.field private static final GEO_SYNC_MAX_INTERVAL_MS:J = 0x3a98L

.field private static final GEO_SYNC_MIN_ALT_DELTA_M:D = 18.0

.field private static final GEO_SYNC_MIN_DISTANCE_M:F = 30.0f

.field private static final GEO_SYNC_MIN_INTERVAL_MS:J = 0xfa0L

.field private static final REQ_CAMERA:I = 0x2b

.field private static final REQ_LOCATION:I = 0x2a

.field private static final SESSION_RETRY_COOLDOWN_MS:J = 0x1388L

.field private static final SHARED_MAP_ZOOM_LEVEL:I = 0x13


# instance fields
.field private cameraPreviewView:Lio/peakmood/mobile/CameraPreviewView;

.field private connectionDialogVisible:Z

.field private currentHitsLeft:I

.field private currentNodeHp:I

.field private currentNodeId:Ljava/lang/String;

.field private currentNodeLat:D

.field private currentNodeLon:D

.field private currentTier:Ljava/lang/String;

.field private deviceId:Ljava/lang/String;

.field private encounterDetailsText:Landroid/widget/TextView;

.field private encounterLootText:Landroid/widget/TextView;

.field private encounterMapView:Lio/peakmood/mobile/WorldMapView;

.field private encounterScreen:Landroid/view/View;

.field private encounterStatusText:Landroid/widget/TextView;

.field private encounterVisible:Z

.field private hasLastLocation:Z

.field private hitInFlight:Z

.field private lastAlt:D

.field private lastGeoSyncAtMs:J

.field private lastGeoSyncLocation:Landroid/location/Location;

.field private lastLat:D

.field private lastLon:D

.field private lastSessionAttemptAtMs:J

.field private leaveEncounterButton:Landroid/widget/Button;

.field private liveLocation:Landroid/location/Location;

.field private final liveLocationListener:Landroid/location/LocationListener;

.field private locationManager:Landroid/location/LocationManager;

.field private miningSceneView:Lio/peakmood/mobile/MiningSceneView;

.field private nodeProgress:Landroid/widget/ProgressBar;

.field private nodeTitleText:Landroid/widget/TextView;

.field private openInFlight:Z

.field private resumeEncounterButton:Landroid/widget/Button;

.field private roamCoordsText:Landroid/widget/TextView;

.field private roamDetailsText:Landroid/widget/TextView;

.field private roamLootText:Landroid/widget/TextView;

.field private roamMapMetaText:Landroid/widget/TextView;

.field private roamMapView:Lio/peakmood/mobile/WorldMapView;

.field private roamScreen:Landroid/view/View;

.field private roamStatusText:Landroid/widget/TextView;

.field private scanInFlight:Z

.field private sessionInFlight:Z

.field private sessionToken:Ljava/lang/String;

.field private terrainModel:Lio/peakmood/mobile/TerrainModel;


# direct methods
.method public constructor <init>()V
    .locals 3

    .line 33
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    .line 67
    const-string v0, "none"

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    .line 68
    const/4 v0, 0x0

    iput v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    .line 69
    iput v0, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    .line 70
    const-wide/high16 v1, 0x7ff8000000000000L    # Double.NaN

    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLat:D

    .line 71
    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLon:D

    .line 73
    const-wide/16 v1, 0x0

    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->lastLat:D

    .line 74
    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->lastLon:D

    .line 75
    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->lastAlt:D

    .line 76
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hasLastLocation:Z

    .line 77
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->encounterVisible:Z

    .line 78
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    .line 79
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->scanInFlight:Z

    .line 80
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    .line 81
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    .line 82
    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->connectionDialogVisible:Z

    .line 83
    const-wide/16 v0, 0x0

    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastSessionAttemptAtMs:J

    .line 84
    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncAtMs:J

    .line 87
    new-instance v0, Lio/peakmood/mobile/MainActivity$1;

    invoke-direct {v0, p0}, Lio/peakmood/mobile/MainActivity$1;-><init>(Lio/peakmood/mobile/MainActivity;)V

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->liveLocationListener:Landroid/location/LocationListener;

    return-void
.end method

.method static synthetic access$000(Lio/peakmood/mobile/MainActivity;Landroid/location/Location;)V
    .locals 0

    .line 33
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->applyLiveLocation(Landroid/location/Location;)V

    return-void
.end method

.method static synthetic access$100(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;
    .locals 0

    .line 33
    iget-object p0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    return-object p0
.end method

.method static synthetic access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 0

    .line 33
    invoke-direct {p0, p1, p2, p3}, Lio/peakmood/mobile/MainActivity;->setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$1100(Lio/peakmood/mobile/MainActivity;)Landroid/location/Location;
    .locals 0

    .line 33
    iget-object p0, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    return-object p0
.end method

.method static synthetic access$1200(Lio/peakmood/mobile/MainActivity;Landroid/location/Location;Z)V
    .locals 0

    .line 33
    invoke-direct {p0, p1, p2}, Lio/peakmood/mobile/MainActivity;->triggerGeoSync(Landroid/location/Location;Z)V

    return-void
.end method

.method static synthetic access$1300(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showConnectionFailure()V

    return-void
.end method

.method static synthetic access$1400(Lio/peakmood/mobile/MainActivity;ILorg/json/JSONObject;)V
    .locals 0

    .line 33
    invoke-direct {p0, p1, p2}, Lio/peakmood/mobile/MainActivity;->handleScanResponse(ILorg/json/JSONObject;)V

    return-void
.end method

.method static synthetic access$1500(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V
    .locals 0

    .line 33
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->showError(Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$1602(Lio/peakmood/mobile/MainActivity;Z)Z
    .locals 0

    .line 33
    iput-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    return p1
.end method

.method static synthetic access$1700(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->resetNodeUi()V

    return-void
.end method

.method static synthetic access$1800(Lio/peakmood/mobile/MainActivity;)I
    .locals 0

    .line 33
    iget p0, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    return p0
.end method

.method static synthetic access$1802(Lio/peakmood/mobile/MainActivity;I)I
    .locals 0

    .line 33
    iput p1, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    return p1
.end method

.method static synthetic access$1900(Lio/peakmood/mobile/MainActivity;)I
    .locals 0

    .line 33
    iget p0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    return p0
.end method

.method static synthetic access$200(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showEncounterMode()V

    return-void
.end method

.method static synthetic access$2000(Lio/peakmood/mobile/MainActivity;)Landroid/widget/ProgressBar;
    .locals 0

    .line 33
    iget-object p0, p0, Lio/peakmood/mobile/MainActivity;->nodeProgress:Landroid/widget/ProgressBar;

    return-object p0
.end method

.method static synthetic access$2100(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateMiningScene()V

    return-void
.end method

.method static synthetic access$2200(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->pushMapState()V

    return-void
.end method

.method static synthetic access$2302(Lio/peakmood/mobile/MainActivity;Z)Z
    .locals 0

    .line 33
    iput-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    return p1
.end method

.method static synthetic access$2400(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)Ljava/lang/String;
    .locals 0

    .line 33
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->tierLabel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$2500(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V
    .locals 0

    .line 33
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->setLootText(Ljava/lang/String;)V

    return-void
.end method

.method static synthetic access$2602(Lio/peakmood/mobile/MainActivity;Z)Z
    .locals 0

    .line 33
    iput-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->scanInFlight:Z

    return p1
.end method

.method static synthetic access$2700(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showReconnectDialog()V

    return-void
.end method

.method static synthetic access$2802(Lio/peakmood/mobile/MainActivity;Z)Z
    .locals 0

    .line 33
    iput-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->connectionDialogVisible:Z

    return p1
.end method

.method static synthetic access$2900(Lio/peakmood/mobile/MainActivity;Z)V
    .locals 0

    .line 33
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->ensureSessionConnected(Z)V

    return-void
.end method

.method static synthetic access$300(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showRoamMode()V

    return-void
.end method

.method static synthetic access$400(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->handleMiningTap()V

    return-void
.end method

.method static synthetic access$500(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;
    .locals 0

    .line 33
    iget-object p0, p0, Lio/peakmood/mobile/MainActivity;->deviceId:Ljava/lang/String;

    return-object p0
.end method

.method static synthetic access$600(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;
    .locals 0
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 33
    invoke-direct {p0, p1, p2, p3}, Lio/peakmood/mobile/MainActivity;->postJson(Ljava/lang/String;Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p0

    return-object p0
.end method

.method static synthetic access$700(Lio/peakmood/mobile/MainActivity;)Ljava/lang/String;
    .locals 0

    .line 33
    iget-object p0, p0, Lio/peakmood/mobile/MainActivity;->sessionToken:Ljava/lang/String;

    return-object p0
.end method

.method static synthetic access$702(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)Ljava/lang/String;
    .locals 0

    .line 33
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity;->sessionToken:Ljava/lang/String;

    return-object p1
.end method

.method static synthetic access$802(Lio/peakmood/mobile/MainActivity;Z)Z
    .locals 0

    .line 33
    iput-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    return p1
.end method

.method static synthetic access$900(Lio/peakmood/mobile/MainActivity;)V
    .locals 0

    .line 33
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    return-void
.end method

.method private applyLiveLocation(Landroid/location/Location;)V
    .locals 2

    .line 518
    new-instance v0, Landroid/location/Location;

    invoke-direct {v0, p1}, Landroid/location/Location;-><init>(Landroid/location/Location;)V

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    .line 519
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->captureLocation(Landroid/location/Location;)V

    .line 520
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->isCurrentNodeStaleFor(Landroid/location/Location;)Z

    move-result p1

    if-eqz p1, :cond_0

    .line 521
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->resetNodeUi()V

    .line 522
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->readAltitude(Landroid/location/Location;)D

    move-result-wide v0

    invoke-direct {p0, v0, v1}, Lio/peakmood/mobile/MainActivity;->formatTerrainDetails(D)Ljava/lang/String;

    move-result-object p1

    const-string v0, "\u041f\u041e\u0418\u0421\u041a"

    const-string v1, "\u0421\u0435\u043a\u0442\u043e\u0440 \u043e\u0431\u043d\u043e\u0432\u043b\u0451\u043d"

    invoke-direct {p0, v1, p1, v0}, Lio/peakmood/mobile/MainActivity;->setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 524
    :cond_0
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-nez p1, :cond_1

    .line 525
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->roamCoordsText:Landroid/widget/TextView;

    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    invoke-direct {p0, v0}, Lio/peakmood/mobile/MainActivity;->formatLocationSummary(Landroid/location/Location;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {p1, v0}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 527
    :cond_1
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->sessionToken:Ljava/lang/String;

    const/4 v0, 0x0

    if-nez p1, :cond_2

    .line 528
    invoke-direct {p0, v0}, Lio/peakmood/mobile/MainActivity;->ensureSessionConnected(Z)V

    .line 529
    return-void

    .line 531
    :cond_2
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-eqz p1, :cond_3

    .line 532
    return-void

    .line 534
    :cond_3
    new-instance p1, Landroid/location/Location;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->liveLocation:Landroid/location/Location;

    invoke-direct {p1, v1}, Landroid/location/Location;-><init>(Landroid/location/Location;)V

    invoke-direct {p0, p1, v0}, Lio/peakmood/mobile/MainActivity;->triggerGeoSync(Landroid/location/Location;Z)V

    .line 535
    return-void
.end method

.method private bestLastKnownLocation()Landroid/location/Location;
    .locals 13

    .line 416
    nop

    .line 417
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 418
    const/4 v2, 0x3

    new-array v3, v2, [Ljava/lang/String;

    const/4 v4, 0x0

    const-string v5, "gps"

    aput-object v5, v3, v4

    const-string v5, "network"

    const/4 v6, 0x1

    aput-object v5, v3, v6

    const-string v5, "passive"

    const/4 v6, 0x2

    aput-object v5, v3, v6

    .line 423
    const/4 v5, 0x0

    move-object v6, v5

    :goto_0
    if-ge v4, v2, :cond_4

    aget-object v7, v3, v4

    .line 425
    :try_start_0
    iget-object v8, p0, Lio/peakmood/mobile/MainActivity;->locationManager:Landroid/location/LocationManager;

    invoke-virtual {v8, v7}, Landroid/location/LocationManager;->getLastKnownLocation(Ljava/lang/String;)Landroid/location/Location;

    move-result-object v7

    .line 426
    if-nez v7, :cond_0

    .line 427
    goto :goto_1

    .line 429
    :cond_0
    invoke-virtual {v7}, Landroid/location/Location;->getTime()J

    move-result-wide v8

    sub-long v8, v0, v8

    const-wide/16 v10, 0x3a98

    cmp-long v12, v8, v10

    if-lez v12, :cond_1

    .line 430
    goto :goto_1

    .line 432
    :cond_1
    if-eqz v6, :cond_2

    invoke-virtual {v7}, Landroid/location/Location;->getTime()J

    move-result-wide v8

    invoke-virtual {v6}, Landroid/location/Location;->getTime()J

    move-result-wide v10
    :try_end_0
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_0

    cmp-long v12, v8, v10

    if-lez v12, :cond_3

    .line 433
    :cond_2
    move-object v6, v7

    .line 437
    :cond_3
    nop

    .line 423
    :goto_1
    add-int/lit8 v4, v4, 0x1

    goto :goto_0

    .line 435
    :catch_0
    move-exception v0

    .line 436
    return-object v5

    .line 439
    :cond_4
    return-object v6
.end method

.method private bindViews()V
    .locals 1

    .line 142
    const/high16 v0, 0x7f080000

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamScreen:Landroid/view/View;

    .line 143
    const v0, 0x7f08000b

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterScreen:Landroid/view/View;

    .line 144
    const v0, 0x7f080004

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamStatusText:Landroid/widget/TextView;

    .line 145
    const v0, 0x7f080005

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamCoordsText:Landroid/widget/TextView;

    .line 146
    const v0, 0x7f080006

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamDetailsText:Landroid/widget/TextView;

    .line 147
    const v0, 0x7f08000a

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamLootText:Landroid/widget/TextView;

    .line 148
    const v0, 0x7f080007

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamMapMetaText:Landroid/widget/TextView;

    .line 149
    const v0, 0x7f080014

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterStatusText:Landroid/widget/TextView;

    .line 150
    const v0, 0x7f080015

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterDetailsText:Landroid/widget/TextView;

    .line 151
    const v0, 0x7f080018

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterLootText:Landroid/widget/TextView;

    .line 152
    const v0, 0x7f080013

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/TextView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->nodeTitleText:Landroid/widget/TextView;

    .line 153
    const v0, 0x7f080016

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/ProgressBar;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->nodeProgress:Landroid/widget/ProgressBar;

    .line 154
    const v0, 0x7f080008

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/Button;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->resumeEncounterButton:Landroid/widget/Button;

    .line 155
    const v0, 0x7f08000f

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Landroid/widget/Button;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->leaveEncounterButton:Landroid/widget/Button;

    .line 156
    const v0, 0x7f08000c

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Lio/peakmood/mobile/CameraPreviewView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->cameraPreviewView:Lio/peakmood/mobile/CameraPreviewView;

    .line 157
    const v0, 0x7f080012

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Lio/peakmood/mobile/MiningSceneView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->miningSceneView:Lio/peakmood/mobile/MiningSceneView;

    .line 158
    const v0, 0x7f080001

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Lio/peakmood/mobile/WorldMapView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamMapView:Lio/peakmood/mobile/WorldMapView;

    .line 159
    const v0, 0x7f080011

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v0

    check-cast v0, Lio/peakmood/mobile/WorldMapView;

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterMapView:Lio/peakmood/mobile/WorldMapView;

    .line 160
    return-void
.end method

.method private captureLocation(Landroid/location/Location;)V
    .locals 2

    .line 538
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hasLastLocation:Z

    .line 539
    invoke-virtual {p1}, Landroid/location/Location;->getLatitude()D

    move-result-wide v0

    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastLat:D

    .line 540
    invoke-virtual {p1}, Landroid/location/Location;->getLongitude()D

    move-result-wide v0

    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastLon:D

    .line 541
    invoke-virtual {p1}, Landroid/location/Location;->hasAltitude()Z

    move-result v0

    if-eqz v0, :cond_0

    invoke-virtual {p1}, Landroid/location/Location;->getAltitude()D

    move-result-wide v0

    goto :goto_0

    :cond_0
    const-wide/16 v0, 0x0

    :goto_0
    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastAlt:D

    .line 542
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->pushMapState()V

    .line 543
    return-void
.end method

.method private configureButtons()V
    .locals 2

    .line 163
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->resumeEncounterButton:Landroid/widget/Button;

    new-instance v1, Lio/peakmood/mobile/MainActivity$2;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$2;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 171
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->leaveEncounterButton:Landroid/widget/Button;

    new-instance v1, Lio/peakmood/mobile/MainActivity$3;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$3;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 177
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->miningSceneView:Lio/peakmood/mobile/MiningSceneView;

    new-instance v1, Lio/peakmood/mobile/MainActivity$4;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$4;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-virtual {v0, v1}, Lio/peakmood/mobile/MiningSceneView;->setOnNodeTapListener(Lio/peakmood/mobile/MiningSceneView$OnNodeTapListener;)V

    .line 183
    return-void
.end method

.method private configureMapViews()V
    .locals 2

    .line 186
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamMapView:Lio/peakmood/mobile/WorldMapView;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Lio/peakmood/mobile/WorldMapView;->setViewportMode(I)V

    .line 187
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterMapView:Lio/peakmood/mobile/WorldMapView;

    invoke-virtual {v0, v1}, Lio/peakmood/mobile/WorldMapView;->setViewportMode(I)V

    .line 188
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamMapView:Lio/peakmood/mobile/WorldMapView;

    const/16 v1, 0x13

    invoke-virtual {v0, v1}, Lio/peakmood/mobile/WorldMapView;->setZoomLevelOverride(I)V

    .line 189
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterMapView:Lio/peakmood/mobile/WorldMapView;

    invoke-virtual {v0, v1}, Lio/peakmood/mobile/WorldMapView;->setZoomLevelOverride(I)V

    .line 190
    return-void
.end method

.method private ensureCameraPermission()V
    .locals 3

    .line 283
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->hasCameraPermission()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 284
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateCameraPreview()V

    .line 285
    return-void

    .line 287
    :cond_0
    const/4 v0, 0x1

    new-array v0, v0, [Ljava/lang/String;

    const-string v1, "android.permission.CAMERA"

    const/4 v2, 0x0

    aput-object v1, v0, v2

    const/16 v1, 0x2b

    invoke-virtual {p0, v0, v1}, Lio/peakmood/mobile/MainActivity;->requestPermissions([Ljava/lang/String;I)V

    .line 288
    return-void
.end method

.method private ensureLocationBootstrap()V
    .locals 3

    .line 303
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->hasLocationPermission()Z

    move-result v0

    const/4 v1, 0x0

    if-nez v0, :cond_0

    .line 304
    const/4 v0, 0x2

    new-array v0, v0, [Ljava/lang/String;

    const-string v2, "android.permission.ACCESS_FINE_LOCATION"

    aput-object v2, v0, v1

    const-string v1, "android.permission.ACCESS_COARSE_LOCATION"

    const/4 v2, 0x1

    aput-object v1, v0, v2

    const/16 v1, 0x2a

    invoke-virtual {p0, v0, v1}, Lio/peakmood/mobile/MainActivity;->requestPermissions([Ljava/lang/String;I)V

    .line 311
    return-void

    .line 313
    :cond_0
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->startLiveLocationUpdates()V

    .line 314
    invoke-direct {p0, v1}, Lio/peakmood/mobile/MainActivity;->ensureSessionConnected(Z)V

    .line 315
    return-void
.end method

.method private ensureSessionConnected(Z)V
    .locals 6

    .line 318
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->sessionToken:Ljava/lang/String;

    if-nez v0, :cond_3

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    if-eqz v0, :cond_0

    goto :goto_0

    .line 321
    :cond_0
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 322
    if-nez p1, :cond_2

    .line 323
    iget-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->connectionDialogVisible:Z

    if-eqz p1, :cond_1

    .line 324
    return-void

    .line 326
    :cond_1
    iget-wide v2, p0, Lio/peakmood/mobile/MainActivity;->lastSessionAttemptAtMs:J

    sub-long v2, v0, v2

    const-wide/16 v4, 0x1388

    cmp-long p1, v2, v4

    if-gez p1, :cond_2

    .line 327
    return-void

    .line 330
    :cond_2
    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastSessionAttemptAtMs:J

    .line 331
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->openSession()V

    .line 332
    return-void

    .line 319
    :cond_3
    :goto_0
    return-void
.end method

.method private formatLocationSummary(Landroid/location/Location;)Ljava/lang/String;
    .locals 22

    .line 915
    move-object/from16 v0, p0

    invoke-virtual/range {p1 .. p1}, Landroid/location/Location;->getLatitude()D

    move-result-wide v1

    .line 916
    invoke-virtual/range {p1 .. p1}, Landroid/location/Location;->getLongitude()D

    move-result-wide v3

    .line 917
    invoke-virtual/range {p1 .. p1}, Landroid/location/Location;->hasAltitude()Z

    move-result v5

    const-wide/16 v6, 0x0

    if-eqz v5, :cond_0

    invoke-virtual/range {p1 .. p1}, Landroid/location/Location;->getAltitude()D

    move-result-wide v8

    goto :goto_0

    :cond_0
    move-wide v8, v6

    .line 918
    :goto_0
    invoke-direct/range {p0 .. p1}, Lio/peakmood/mobile/MainActivity;->terrainSnapshotFor(Landroid/location/Location;)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;

    move-result-object v5

    .line 919
    const/4 v10, 0x5

    const/4 v11, 0x4

    const/4 v12, 0x3

    const/4 v13, 0x2

    const/4 v14, 0x1

    const/4 v15, 0x0

    const-string v16, "\u0412"

    const-string v17, "\u0417"

    const-string v18, "\u0421"

    const-string v19, "\u042e"

    if-nez v5, :cond_3

    .line 920
    sget-object v5, Ljava/util/Locale;->US:Ljava/util/Locale;

    .line 923
    cmpl-double v20, v1, v6

    if-ltz v20, :cond_1

    goto :goto_1

    :cond_1
    move-object/from16 v18, v19

    .line 924
    :goto_1
    invoke-static {v1, v2}, Ljava/lang/Math;->abs(D)D

    move-result-wide v1

    invoke-static {v1, v2}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v1

    .line 925
    cmpl-double v2, v3, v6

    if-ltz v2, :cond_2

    goto :goto_2

    :cond_2
    move-object/from16 v16, v17

    .line 926
    :goto_2
    invoke-static {v3, v4}, Ljava/lang/Math;->abs(D)D

    move-result-wide v2

    invoke-static {v2, v3}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v2

    .line 927
    invoke-static {v8, v9}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v3

    new-array v4, v10, [Ljava/lang/Object;

    aput-object v18, v4, v15

    aput-object v1, v4, v14

    aput-object v16, v4, v13

    aput-object v2, v4, v12

    aput-object v3, v4, v11

    .line 920
    const-string v1, "%s %.4f \u00b7 %s %.4f \u00b7 %.0f \u043c"

    invoke-static {v5, v1, v4}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    return-object v1

    .line 930
    :cond_3
    move-wide/from16 v20, v6

    sget-object v6, Ljava/util/Locale;->US:Ljava/util/Locale;

    .line 933
    cmpl-double v7, v1, v20

    if-ltz v7, :cond_4

    goto :goto_3

    :cond_4
    move-object/from16 v18, v19

    .line 934
    :goto_3
    invoke-static {v1, v2}, Ljava/lang/Math;->abs(D)D

    move-result-wide v1

    invoke-static {v1, v2}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v1

    .line 935
    cmpl-double v2, v3, v20

    if-ltz v2, :cond_5

    goto :goto_4

    :cond_5
    move-object/from16 v16, v17

    .line 936
    :goto_4
    invoke-static {v3, v4}, Ljava/lang/Math;->abs(D)D

    move-result-wide v2

    invoke-static {v2, v3}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v2

    .line 937
    invoke-direct {v0, v8, v9}, Lio/peakmood/mobile/MainActivity;->formatSignedMeters(D)Ljava/lang/String;

    move-result-object v3

    iget v4, v5, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->expectedElevationM:I

    const/16 p1, 0x5

    const/4 v7, 0x4

    int-to-double v10, v4

    .line 938
    invoke-direct {v0, v10, v11}, Lio/peakmood/mobile/MainActivity;->formatSignedMeters(D)Ljava/lang/String;

    move-result-object v4

    iget v5, v5, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->expectedElevationM:I

    .line 939
    invoke-static {v5}, Ljava/lang/Math;->abs(I)I

    move-result v5

    int-to-double v10, v5

    invoke-static {v8, v9}, Ljava/lang/Math;->abs(D)D

    move-result-wide v8

    invoke-static {v10, v11}, Ljava/lang/Double;->isNaN(D)Z

    sub-double/2addr v10, v8

    invoke-static {v10, v11}, Ljava/lang/Math;->abs(D)D

    move-result-wide v8

    invoke-static {v8, v9}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v5

    const/4 v8, 0x7

    new-array v8, v8, [Ljava/lang/Object;

    aput-object v18, v8, v15

    aput-object v1, v8, v14

    aput-object v16, v8, v13

    aput-object v2, v8, v12

    aput-object v3, v8, v7

    aput-object v4, v8, p1

    const/4 v1, 0x6

    aput-object v5, v8, v1

    .line 930
    const-string v1, "%s %.4f \u00b7 %s %.4f\nGPS %s \u00b7 \u043a\u0430\u0440\u0442\u0430 %s \u00b7 \u0394mod %.0f \u043c"

    invoke-static {v6, v1, v8}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    return-object v1
.end method

.method private formatSignedMeters(D)Ljava/lang/String;
    .locals 2

    .line 878
    sget-object v0, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-static {p1, p2}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p1

    const/4 p2, 0x1

    new-array p2, p2, [Ljava/lang/Object;

    const/4 v1, 0x0

    aput-object p1, p2, v1

    const-string p1, "%+.0f \u043c"

    invoke-static {v0, p1, p2}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    return-object p1
.end method

.method private formatTerrainDetails(D)Ljava/lang/String;
    .locals 11

    .line 860
    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hasLastLocation:Z

    const-string v1, "GPS %s"

    const/4 v2, 0x0

    const/4 v3, 0x1

    if-nez v0, :cond_0

    .line 861
    sget-object v0, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-direct {p0, p1, p2}, Lio/peakmood/mobile/MainActivity;->formatSignedMeters(D)Ljava/lang/String;

    move-result-object p1

    new-array p2, v3, [Ljava/lang/Object;

    aput-object p1, p2, v2

    invoke-static {v0, v1, p2}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    return-object p1

    .line 863
    :cond_0
    iget-wide v5, p0, Lio/peakmood/mobile/MainActivity;->lastLat:D

    iget-wide v7, p0, Lio/peakmood/mobile/MainActivity;->lastLon:D

    move-object v4, p0

    move-wide v9, p1

    invoke-direct/range {v4 .. v10}, Lio/peakmood/mobile/MainActivity;->terrainSnapshotFor(DDD)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;

    move-result-object p1

    .line 864
    if-nez p1, :cond_1

    .line 865
    sget-object p1, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-direct {p0, v9, v10}, Lio/peakmood/mobile/MainActivity;->formatSignedMeters(D)Ljava/lang/String;

    move-result-object p2

    new-array v0, v3, [Ljava/lang/Object;

    aput-object p2, v0, v2

    invoke-static {p1, v1, v0}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    return-object p1

    .line 867
    :cond_1
    sget-object p2, Ljava/util/Locale;->US:Ljava/util/Locale;

    iget-object v0, p1, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->label:Ljava/lang/String;

    .line 871
    invoke-direct {p0, v9, v10}, Lio/peakmood/mobile/MainActivity;->formatSignedMeters(D)Ljava/lang/String;

    move-result-object v1

    iget v5, p1, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->expectedElevationM:I

    int-to-double v5, v5

    .line 872
    invoke-direct {p0, v5, v6}, Lio/peakmood/mobile/MainActivity;->formatSignedMeters(D)Ljava/lang/String;

    move-result-object v5

    iget p1, p1, Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;->expectedElevationM:I

    .line 873
    invoke-static {p1}, Ljava/lang/Math;->abs(I)I

    move-result p1

    int-to-double v6, p1

    invoke-static {v9, v10}, Ljava/lang/Math;->abs(D)D

    move-result-wide v8

    invoke-static {v6, v7}, Ljava/lang/Double;->isNaN(D)Z

    sub-double/2addr v6, v8

    invoke-static {v6, v7}, Ljava/lang/Math;->abs(D)D

    move-result-wide v6

    invoke-static {v6, v7}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p1

    const/4 v6, 0x4

    new-array v6, v6, [Ljava/lang/Object;

    aput-object v0, v6, v2

    aput-object v1, v6, v3

    const/4 v0, 0x2

    aput-object v5, v6, v0

    const/4 v0, 0x3

    aput-object p1, v6, v0

    .line 867
    const-string p1, "%s \u00b7 GPS %s \u00b7 \u043a\u0430\u0440\u0442\u0430 %s \u00b7 \u0394mod %.0f \u043c"

    invoke-static {p2, p1, v6}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    return-object p1
.end method

.method private handleMiningTap()V
    .locals 1

    .line 266
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-eqz v0, :cond_4

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    if-nez v0, :cond_4

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    if-nez v0, :cond_4

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    if-eqz v0, :cond_0

    goto :goto_0

    .line 269
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->miningSceneView:Lio/peakmood/mobile/MiningSceneView;

    invoke-virtual {v0}, Lio/peakmood/mobile/MiningSceneView;->isImpactAnimationRunning()Z

    move-result v0

    if-eqz v0, :cond_1

    .line 270
    return-void

    .line 272
    :cond_1
    iget v0, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    if-lez v0, :cond_3

    .line 273
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->miningSceneView:Lio/peakmood/mobile/MiningSceneView;

    invoke-virtual {v0}, Lio/peakmood/mobile/MiningSceneView;->triggerImpact()Z

    move-result v0

    if-nez v0, :cond_2

    .line 274
    return-void

    .line 276
    :cond_2
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->hitNode()V

    .line 277
    return-void

    .line 279
    :cond_3
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->openNode()V

    .line 280
    return-void

    .line 267
    :cond_4
    :goto_0
    return-void
.end method

.method private handleScanResponse(ILorg/json/JSONObject;)V
    .locals 9

    .line 553
    const/4 v0, 0x0

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->scanInFlight:Z

    .line 554
    const/16 v1, 0x190

    if-lt p1, v1, :cond_1

    .line 555
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->resetNodeUi()V

    .line 556
    nop

    .line 558
    iget-boolean p1, p0, Lio/peakmood/mobile/MainActivity;->hasLastLocation:Z

    if-eqz p1, :cond_0

    iget-wide p1, p0, Lio/peakmood/mobile/MainActivity;->lastAlt:D

    invoke-direct {p0, p1, p2}, Lio/peakmood/mobile/MainActivity;->formatTerrainDetails(D)Ljava/lang/String;

    move-result-object p1

    goto :goto_0

    :cond_0
    const-string p1, "\u0412\u044b\u0441\u043e\u0442\u0430 \u043f\u043e\u043a\u0430 \u043d\u0435 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0430. \u041f\u043e\u0432\u0442\u043e\u0440\u0438 \u0441\u043a\u0430\u043d \u0447\u0435\u0440\u0435\u0437 \u043d\u0435\u0441\u043a\u043e\u043b\u044c\u043a\u043e \u0441\u0435\u043a\u0443\u043d\u0434."

    .line 556
    :goto_0
    const-string p2, "\u0421\u0438\u0433\u043d\u0430\u043b \u043d\u0435 \u043f\u0440\u043e\u0448\u0451\u043b \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0443"

    const-string v0, "\u041f\u0420\u041e\u0412\u0415\u0420\u041a\u0410"

    invoke-direct {p0, p2, p1, v0}, Lio/peakmood/mobile/MainActivity;->setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 561
    const-string p1, "\u0412 \u044d\u0442\u043e\u043c \u0441\u0435\u043a\u0442\u043e\u0440\u0435 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0451\u043d\u043d\u043e\u0439 \u043d\u0430\u0445\u043e\u0434\u043a\u0438."

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->setLootText(Ljava/lang/String;)V

    .line 562
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showRoamMode()V

    .line 563
    return-void

    .line 566
    :cond_1
    const-string p1, "scan"

    invoke-virtual {p2, p1}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object p1

    .line 567
    if-nez p1, :cond_2

    .line 568
    const-string p1, "\u041f\u0443\u0441\u0442\u043e\u0439 \u043e\u0442\u0432\u0435\u0442 \u0441\u0435\u0440\u0432\u0435\u0440\u0430."

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->showError(Ljava/lang/String;)V

    .line 569
    return-void

    .line 572
    :cond_2
    const-string p2, "tier"

    const-string v1, "none"

    invoke-virtual {p1, p2, v1}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    .line 573
    const-string v2, "\u0421\u043a\u0430\u043d \u0437\u0430\u0432\u0435\u0440\u0448\u0451\u043d"

    const-string v3, "display_name"

    invoke-virtual {p1, v3, v2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 574
    const-string v4, "reported_alt_m"

    iget-wide v5, p0, Lio/peakmood/mobile/MainActivity;->lastAlt:D

    invoke-virtual {p1, v4, v5, v6}, Lorg/json/JSONObject;->optDouble(Ljava/lang/String;D)D

    move-result-wide v4

    .line 575
    invoke-direct {p0, v4, v5}, Lio/peakmood/mobile/MainActivity;->formatTerrainDetails(D)Ljava/lang/String;

    move-result-object v6

    .line 577
    invoke-virtual {v1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    const/4 v7, 0x1

    if-eqz v1, :cond_3

    .line 578
    const-string v0, "\u041f\u041e\u0418\u0421\u041a"

    goto :goto_1

    .line 580
    :cond_3
    sget-object v1, Ljava/util/Locale;->US:Ljava/util/Locale;

    .line 583
    invoke-direct {p0, p2}, Lio/peakmood/mobile/MainActivity;->tierLabelUpper(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v8

    .line 584
    invoke-static {v4, v5}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v4

    const/4 v5, 0x2

    new-array v5, v5, [Ljava/lang/Object;

    aput-object v8, v5, v0

    aput-object v4, v5, v7

    .line 580
    const-string v0, "%s \u00b7 %.0f \u043c"

    invoke-static {v1, v0, v5}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    .line 587
    :goto_1
    invoke-direct {p0, v2, v6, v0}, Lio/peakmood/mobile/MainActivity;->setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 589
    const-string v0, "node"

    invoke-virtual {p1, v0}, Lorg/json/JSONObject;->optJSONObject(Ljava/lang/String;)Lorg/json/JSONObject;

    move-result-object v0

    .line 590
    if-nez v0, :cond_4

    .line 591
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->resetNodeUi()V

    .line 592
    const-string p2, "message"

    const-string v0, "\u041d\u043e\u0434\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430."

    invoke-virtual {p1, p2, v0}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->setLootText(Ljava/lang/String;)V

    .line 593
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showRoamMode()V

    .line 594
    return-void

    .line 597
    :cond_4
    iput-object p2, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    .line 598
    const-string p1, "id"

    const/4 p2, 0x0

    invoke-virtual {v0, p1, p2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    iput-object p1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    .line 599
    const-string p1, "hp_total"

    invoke-virtual {v0, p1, v7}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result p1

    iput p1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    .line 600
    const-string p1, "hits_left"

    iget p2, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    invoke-virtual {v0, p1, p2}, Lorg/json/JSONObject;->optInt(Ljava/lang/String;I)I

    move-result p1

    iput p1, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    .line 601
    const-string p1, "lat"

    const-wide/high16 v1, 0x7ff8000000000000L    # Double.NaN

    invoke-virtual {v0, p1, v1, v2}, Lorg/json/JSONObject;->optDouble(Ljava/lang/String;D)D

    move-result-wide p1

    iput-wide p1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLat:D

    .line 602
    const-string p1, "lon"

    invoke-virtual {v0, p1, v1, v2}, Lorg/json/JSONObject;->optDouble(Ljava/lang/String;D)D

    move-result-wide p1

    iput-wide p1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLon:D

    .line 603
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->nodeProgress:Landroid/widget/ProgressBar;

    iget p2, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    invoke-virtual {p1, p2}, Landroid/widget/ProgressBar;->setMax(I)V

    .line 604
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->nodeProgress:Landroid/widget/ProgressBar;

    iget p2, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    iget v1, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    sub-int/2addr p2, v1

    invoke-virtual {p1, p2}, Landroid/widget/ProgressBar;->setProgress(I)V

    .line 605
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->nodeTitleText:Landroid/widget/TextView;

    const-string p2, "\u0416\u0435\u043e\u0434\u0430"

    invoke-virtual {v0, v3, p2}, Lorg/json/JSONObject;->optString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 606
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateMiningScene()V

    .line 607
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 608
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->pushMapState()V

    .line 609
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showRoamMode()V

    .line 610
    return-void
.end method

.method private hasCameraPermission()Z
    .locals 1

    .line 299
    const-string v0, "android.permission.CAMERA"

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_0

    const/4 v0, 0x1

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    :goto_0
    return v0
.end method

.method private hasLocationPermission()Z
    .locals 1

    .line 378
    const-string v0, "android.permission.ACCESS_FINE_LOCATION"

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-eqz v0, :cond_1

    .line 379
    const-string v0, "android.permission.ACCESS_COARSE_LOCATION"

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-nez v0, :cond_0

    goto :goto_0

    :cond_0
    const/4 v0, 0x0

    goto :goto_1

    :cond_1
    :goto_0
    const/4 v0, 0x1

    .line 378
    :goto_1
    return v0
.end method

.method private hitNode()V
    .locals 2

    .line 613
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-eqz v0, :cond_1

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    if-eqz v0, :cond_0

    goto :goto_0

    .line 616
    :cond_0
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    .line 617
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 618
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lio/peakmood/mobile/MainActivity$7;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$7;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    .line 667
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 668
    return-void

    .line 614
    :cond_1
    :goto_0
    return-void
.end method

.method private isCurrentNodeStaleFor(Landroid/location/Location;)Z
    .locals 3

    .line 546
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-eqz v0, :cond_1

    if-nez p1, :cond_0

    goto :goto_0

    .line 549
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->readAltitude(Landroid/location/Location;)D

    move-result-wide v1

    invoke-direct {p0, v1, v2}, Lio/peakmood/mobile/MainActivity;->tierForAltitude(D)Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    xor-int/lit8 p1, p1, 0x1

    return p1

    .line 547
    :cond_1
    :goto_0
    const/4 p1, 0x0

    return p1
.end method

.method private loadOrCreateDeviceId()Ljava/lang/String;
    .locals 3

    .line 193
    const-string v0, "peakmood"

    const/4 v1, 0x0

    invoke-virtual {p0, v0, v1}, Lio/peakmood/mobile/MainActivity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v0

    .line 194
    const/4 v1, 0x0

    const-string v2, "device_id"

    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 195
    if-eqz v1, :cond_0

    .line 196
    return-object v1

    .line 198
    :cond_0
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v1

    invoke-virtual {v1}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v1

    .line 199
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String;Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 200
    return-object v1
.end method

.method private openNode()V
    .locals 2

    .line 671
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-eqz v0, :cond_1

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    if-nez v0, :cond_1

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    if-eqz v0, :cond_0

    goto :goto_0

    .line 674
    :cond_0
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    .line 675
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 676
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lio/peakmood/mobile/MainActivity$8;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$8;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    .line 729
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 730
    return-void

    .line 672
    :cond_1
    :goto_0
    return-void
.end method

.method private openSession()V
    .locals 3

    .line 335
    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    if-eqz v0, :cond_0

    .line 336
    return-void

    .line 338
    :cond_0
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    .line 339
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 340
    const-string v0, "\u0421\u0432\u0435\u0440\u044f\u044e \u043a\u0430\u0440\u0442\u0443, \u043e\u0431\u0437\u043e\u0440 \u0438 \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0438\u0435 \u0441\u0438\u0433\u043d\u0430\u043b\u044b."

    const-string v1, "\u0421\u0412\u042f\u0417\u042c"

    const-string v2, "\u041f\u043e\u0434\u043a\u043b\u044e\u0447\u0430\u044e \u043f\u0440\u043e\u0444\u0438\u043b\u044c\u2026"

    invoke-direct {p0, v2, v0, v1}, Lio/peakmood/mobile/MainActivity;->setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 345
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lio/peakmood/mobile/MainActivity$5;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$5;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    .line 374
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 375
    return-void
.end method

.method private postJson(Ljava/lang/String;Lorg/json/JSONObject;Ljava/lang/String;)Lorg/json/JSONObject;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 744
    new-instance v0, Ljava/net/URL;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const v2, 0x7f060004

    invoke-virtual {p0, v2}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {v0, p1}, Ljava/net/URL;-><init>(Ljava/lang/String;)V

    .line 745
    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;

    move-result-object p1

    check-cast p1, Ljava/net/HttpURLConnection;

    .line 746
    const-string v0, "POST"

    invoke-virtual {p1, v0}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V

    .line 747
    const/16 v0, 0x1770

    invoke-virtual {p1, v0}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V

    .line 748
    invoke-virtual {p1, v0}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V

    .line 749
    const/4 v0, 0x1

    invoke-virtual {p1, v0}, Ljava/net/HttpURLConnection;->setDoOutput(Z)V

    .line 750
    const-string v0, "Content-Type"

    const-string v1, "application/json; charset=utf-8"

    invoke-virtual {p1, v0, v1}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    .line 751
    if-eqz p3, :cond_0

    .line 752
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "Bearer "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p3

    invoke-virtual {p3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p3

    const-string v0, "Authorization"

    invoke-virtual {p1, v0, p3}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    .line 755
    :cond_0
    invoke-virtual {p2}, Lorg/json/JSONObject;->toString()Ljava/lang/String;

    move-result-object p2

    sget-object p3, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {p2, p3}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object p2

    .line 756
    invoke-virtual {p1}, Ljava/net/HttpURLConnection;->getOutputStream()Ljava/io/OutputStream;

    move-result-object p3

    .line 757
    :try_start_0
    invoke-virtual {p3, p2}, Ljava/io/OutputStream;->write([B)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 758
    if-eqz p3, :cond_1

    invoke-virtual {p3}, Ljava/io/OutputStream;->close()V

    .line 760
    :cond_1
    invoke-virtual {p1}, Ljava/net/HttpURLConnection;->getResponseCode()I

    move-result p2

    .line 761
    const/16 p3, 0x190

    if-lt p2, p3, :cond_2

    invoke-virtual {p1}, Ljava/net/HttpURLConnection;->getErrorStream()Ljava/io/InputStream;

    move-result-object p3

    goto :goto_0

    :cond_2
    invoke-virtual {p1}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object p3

    .line 762
    :goto_0
    invoke-direct {p0, p3}, Lio/peakmood/mobile/MainActivity;->readFully(Ljava/io/InputStream;)Ljava/lang/String;

    move-result-object p3

    .line 763
    invoke-virtual {p3}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_3

    new-instance p3, Lorg/json/JSONObject;

    invoke-direct {p3}, Lorg/json/JSONObject;-><init>()V

    goto :goto_1

    :cond_3
    new-instance v0, Lorg/json/JSONObject;

    invoke-direct {v0, p3}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    move-object p3, v0

    .line 764
    :goto_1
    const-string v0, "_http_status"

    invoke-virtual {p3, v0, p2}, Lorg/json/JSONObject;->put(Ljava/lang/String;I)Lorg/json/JSONObject;

    .line 765
    invoke-virtual {p1}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 766
    return-object p3

    .line 756
    :catchall_0
    move-exception p1

    if-eqz p3, :cond_4

    :try_start_1
    invoke-virtual {p3}, Ljava/io/OutputStream;->close()V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    goto :goto_2

    :catchall_1
    move-exception p2

    invoke-static {p1, p2}, Lio/peakmood/mobile/MainActivity$$ExternalSyntheticBackport0;->m(Ljava/lang/Throwable;Ljava/lang/Throwable;)V

    :cond_4
    :goto_2
    throw p1
.end method

.method private pushMapState()V
    .locals 15

    .line 733
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateMiningScene()V

    .line 734
    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hasLastLocation:Z

    if-eqz v0, :cond_0

    .line 735
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->roamMapView:Lio/peakmood/mobile/WorldMapView;

    iget-wide v2, p0, Lio/peakmood/mobile/MainActivity;->lastLat:D

    iget-wide v4, p0, Lio/peakmood/mobile/MainActivity;->lastLon:D

    iget-wide v6, p0, Lio/peakmood/mobile/MainActivity;->lastAlt:D

    invoke-virtual/range {v1 .. v7}, Lio/peakmood/mobile/WorldMapView;->setPlayerLocation(DDD)V

    .line 736
    iget-object v8, p0, Lio/peakmood/mobile/MainActivity;->encounterMapView:Lio/peakmood/mobile/WorldMapView;

    iget-wide v9, p0, Lio/peakmood/mobile/MainActivity;->lastLat:D

    iget-wide v11, p0, Lio/peakmood/mobile/MainActivity;->lastLon:D

    iget-wide v13, p0, Lio/peakmood/mobile/MainActivity;->lastAlt:D

    invoke-virtual/range {v8 .. v14}, Lio/peakmood/mobile/WorldMapView;->setPlayerLocation(DDD)V

    .line 738
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-eqz v0, :cond_1

    const/4 v0, 0x1

    const/4 v2, 0x1

    goto :goto_0

    :cond_1
    const/4 v0, 0x0

    const/4 v2, 0x0

    .line 739
    :goto_0
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->roamMapView:Lio/peakmood/mobile/WorldMapView;

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    iget-object v4, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    iget v5, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    iget v6, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    iget-wide v7, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLat:D

    iget-wide v9, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLon:D

    invoke-virtual/range {v1 .. v10}, Lio/peakmood/mobile/WorldMapView;->setNodeState(ZLjava/lang/String;Ljava/lang/String;IIDD)V

    .line 740
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->encounterMapView:Lio/peakmood/mobile/WorldMapView;

    iget-object v3, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    iget-object v4, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    iget v5, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    iget v6, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    iget-wide v7, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLat:D

    iget-wide v9, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLon:D

    invoke-virtual/range {v1 .. v10}, Lio/peakmood/mobile/WorldMapView;->setNodeState(ZLjava/lang/String;Ljava/lang/String;IIDD)V

    .line 741
    return-void
.end method

.method private readAltitude(Landroid/location/Location;)D
    .locals 2

    .line 842
    invoke-virtual {p1}, Landroid/location/Location;->hasAltitude()Z

    move-result v0

    if-eqz v0, :cond_0

    invoke-virtual {p1}, Landroid/location/Location;->getAltitude()D

    move-result-wide v0

    goto :goto_0

    :cond_0
    const-wide/16 v0, 0x0

    :goto_0
    return-wide v0
.end method

.method private readFully(Ljava/io/InputStream;)Ljava/lang/String;
    .locals 3
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 770
    if-nez p1, :cond_0

    .line 771
    const-string p1, ""

    return-object p1

    .line 773
    :cond_0
    new-instance v0, Ljava/io/BufferedReader;

    new-instance v1, Ljava/io/InputStreamReader;

    sget-object v2, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v1, p1, v2}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;Ljava/nio/charset/Charset;)V

    invoke-direct {v0, v1}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 774
    :try_start_0
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    .line 776
    :goto_0
    invoke-virtual {v0}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v1

    if-eqz v1, :cond_1

    .line 777
    invoke-virtual {p1, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    goto :goto_0

    .line 779
    :cond_1
    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    .line 780
    invoke-virtual {v0}, Ljava/io/BufferedReader;->close()V

    .line 779
    return-object p1

    .line 773
    :catchall_0
    move-exception p1

    :try_start_1
    invoke-virtual {v0}, Ljava/io/BufferedReader;->close()V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    goto :goto_1

    :catchall_1
    move-exception v0

    invoke-static {p1, v0}, Lio/peakmood/mobile/MainActivity$$ExternalSyntheticBackport0;->m(Ljava/lang/Throwable;Ljava/lang/Throwable;)V

    :goto_1
    goto :goto_3

    :goto_2
    throw p1

    :goto_3
    goto :goto_2
.end method

.method private refreshActionButtons()V
    .locals 4

    .line 226
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->resumeEncounterButton:Landroid/widget/Button;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    const/4 v2, 0x1

    const/4 v3, 0x0

    if-eqz v1, :cond_0

    iget-boolean v1, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    if-nez v1, :cond_0

    const/4 v1, 0x1

    goto :goto_0

    :cond_0
    const/4 v1, 0x0

    :goto_0
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setEnabled(Z)V

    .line 227
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->leaveEncounterButton:Landroid/widget/Button;

    iget-boolean v1, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    if-nez v1, :cond_1

    iget-boolean v1, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    if-nez v1, :cond_1

    goto :goto_1

    :cond_1
    const/4 v2, 0x0

    :goto_1
    invoke-virtual {v0, v2}, Landroid/widget/Button;->setEnabled(Z)V

    .line 228
    return-void
.end method

.method private resetNodeUi()V
    .locals 3

    .line 244
    const/4 v0, 0x0

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    .line 245
    const-string v0, "none"

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    .line 246
    const/4 v0, 0x0

    iput v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    .line 247
    iput v0, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    .line 248
    const-wide/high16 v1, 0x7ff8000000000000L    # Double.NaN

    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLat:D

    .line 249
    iput-wide v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeLon:D

    .line 250
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->nodeProgress:Landroid/widget/ProgressBar;

    const/4 v2, 0x5

    invoke-virtual {v1, v2}, Landroid/widget/ProgressBar;->setMax(I)V

    .line 251
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->nodeProgress:Landroid/widget/ProgressBar;

    invoke-virtual {v1, v0}, Landroid/widget/ProgressBar;->setProgress(I)V

    .line 252
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->nodeTitleText:Landroid/widget/TextView;

    const v1, 0x7f060009

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(I)V

    .line 253
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->nodeTitleText:Landroid/widget/TextView;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setVisibility(I)V

    .line 254
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->miningSceneView:Lio/peakmood/mobile/MiningSceneView;

    invoke-virtual {v0}, Lio/peakmood/mobile/MiningSceneView;->clearNode()V

    .line 255
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateResumeEncounterButton()V

    .line 256
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 257
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->pushMapState()V

    .line 258
    return-void
.end method

.method private setLootText(Ljava/lang/String;)V
    .locals 1

    .line 231
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamLootText:Landroid/widget/TextView;

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 232
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterLootText:Landroid/widget/TextView;

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 233
    return-void
.end method

.method private setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V
    .locals 1

    .line 236
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamStatusText:Landroid/widget/TextView;

    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 237
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamDetailsText:Landroid/widget/TextView;

    invoke-virtual {v0, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 238
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamMapMetaText:Landroid/widget/TextView;

    invoke-virtual {v0, p3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 239
    iget-object p3, p0, Lio/peakmood/mobile/MainActivity;->encounterStatusText:Landroid/widget/TextView;

    invoke-virtual {p3, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 240
    iget-object p1, p0, Lio/peakmood/mobile/MainActivity;->encounterDetailsText:Landroid/widget/TextView;

    invoke-virtual {p1, p2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 241
    return-void
.end method

.method private showConnectionFailure()V
    .locals 1

    .line 797
    new-instance v0, Lio/peakmood/mobile/MainActivity$10;

    invoke-direct {v0, p0}, Lio/peakmood/mobile/MainActivity$10;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 807
    return-void
.end method

.method private showEncounterMode()V
    .locals 2

    .line 213
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->encounterVisible:Z

    .line 214
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamScreen:Landroid/view/View;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/view/View;->setVisibility(I)V

    .line 215
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterScreen:Landroid/view/View;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/view/View;->setVisibility(I)V

    .line 216
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateCameraPreview()V

    .line 217
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateResumeEncounterButton()V

    .line 218
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 219
    return-void
.end method

.method private showError(Ljava/lang/String;)V
    .locals 1

    .line 784
    new-instance v0, Lio/peakmood/mobile/MainActivity$9;

    invoke-direct {v0, p0, p1}, Lio/peakmood/mobile/MainActivity$9;-><init>(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lio/peakmood/mobile/MainActivity;->runOnUiThread(Ljava/lang/Runnable;)V

    .line 794
    return-void
.end method

.method private showReconnectDialog()V
    .locals 3

    .line 810
    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->connectionDialogVisible:Z

    if-nez v0, :cond_1

    invoke-virtual {p0}, Lio/peakmood/mobile/MainActivity;->isFinishing()Z

    move-result v0

    if-nez v0, :cond_1

    invoke-virtual {p0}, Lio/peakmood/mobile/MainActivity;->isDestroyed()Z

    move-result v0

    if-eqz v0, :cond_0

    goto :goto_0

    .line 813
    :cond_0
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->connectionDialogVisible:Z

    .line 814
    new-instance v1, Landroid/app/AlertDialog$Builder;

    invoke-direct {v1, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    .line 815
    const v2, 0x7f06001a

    invoke-virtual {v1, v2}, Landroid/app/AlertDialog$Builder;->setTitle(I)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    .line 816
    const v2, 0x7f06001b

    invoke-virtual {v1, v2}, Landroid/app/AlertDialog$Builder;->setMessage(I)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    .line 817
    invoke-virtual {v1, v0}, Landroid/app/AlertDialog$Builder;->setCancelable(Z)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lio/peakmood/mobile/MainActivity$12;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$12;-><init>(Lio/peakmood/mobile/MainActivity;)V

    .line 818
    const v2, 0x7f06001c

    invoke-virtual {v0, v2, v1}, Landroid/app/AlertDialog$Builder;->setPositiveButton(ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lio/peakmood/mobile/MainActivity$11;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$11;-><init>(Lio/peakmood/mobile/MainActivity;)V

    .line 825
    const v2, 0x7f06001d

    invoke-virtual {v0, v2, v1}, Landroid/app/AlertDialog$Builder;->setNegativeButton(ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 831
    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->create()Landroid/app/AlertDialog;

    move-result-object v0

    .line 832
    new-instance v1, Lio/peakmood/mobile/MainActivity$13;

    invoke-direct {v1, p0}, Lio/peakmood/mobile/MainActivity$13;-><init>(Lio/peakmood/mobile/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog;->setOnDismissListener(Landroid/content/DialogInterface$OnDismissListener;)V

    .line 838
    invoke-virtual {v0}, Landroid/app/AlertDialog;->show()V

    .line 839
    return-void

    .line 811
    :cond_1
    :goto_0
    return-void
.end method

.method private showRoamMode()V
    .locals 2

    .line 204
    const/4 v0, 0x0

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->encounterVisible:Z

    .line 205
    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->roamScreen:Landroid/view/View;

    invoke-virtual {v1, v0}, Landroid/view/View;->setVisibility(I)V

    .line 206
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->encounterScreen:Landroid/view/View;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/view/View;->setVisibility(I)V

    .line 207
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateCameraPreview()V

    .line 208
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateResumeEncounterButton()V

    .line 209
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 210
    return-void
.end method

.method private startLiveLocationUpdates()V
    .locals 11

    .line 482
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->hasLocationPermission()Z

    move-result v0

    if-nez v0, :cond_0

    .line 483
    return-void

    .line 486
    :cond_0
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->stopLiveLocationUpdates()V

    .line 487
    const/4 v1, 0x3

    new-array v2, v1, [Ljava/lang/String;

    const-string v0, "gps"

    const/4 v3, 0x0

    aput-object v0, v2, v3

    const-string v0, "network"

    const/4 v4, 0x1

    aput-object v0, v2, v4

    const-string v0, "passive"

    const/4 v4, 0x2

    aput-object v0, v2, v4

    .line 492
    nop

    :goto_0
    if-ge v3, v1, :cond_2

    aget-object v5, v2, v3

    .line 494
    :try_start_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->locationManager:Landroid/location/LocationManager;

    invoke-virtual {v0, v5}, Landroid/location/LocationManager;->isProviderEnabled(Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_1

    .line 495
    goto :goto_1

    .line 497
    :cond_1
    iget-object v4, p0, Lio/peakmood/mobile/MainActivity;->locationManager:Landroid/location/LocationManager;

    iget-object v9, p0, Lio/peakmood/mobile/MainActivity;->liveLocationListener:Landroid/location/LocationListener;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v10

    const-wide/16 v6, 0x3e8

    const/4 v8, 0x0

    invoke-virtual/range {v4 .. v10}, Landroid/location/LocationManager;->requestLocationUpdates(Ljava/lang/String;JFLandroid/location/LocationListener;Landroid/os/Looper;)V
    :try_end_0
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_1
    .catch Ljava/lang/IllegalArgumentException; {:try_start_0 .. :try_end_0} :catch_0

    .line 501
    goto :goto_1

    .line 500
    :catch_0
    move-exception v0

    .line 492
    :goto_1
    add-int/lit8 v3, v3, 0x1

    goto :goto_0

    .line 498
    :catch_1
    move-exception v0

    .line 499
    return-void

    .line 504
    :cond_2
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->bestLastKnownLocation()Landroid/location/Location;

    move-result-object v0

    .line 505
    if-eqz v0, :cond_3

    .line 506
    invoke-direct {p0, v0}, Lio/peakmood/mobile/MainActivity;->applyLiveLocation(Landroid/location/Location;)V

    .line 508
    :cond_3
    return-void
.end method

.method private stopLiveLocationUpdates()V
    .locals 2

    .line 512
    :try_start_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->locationManager:Landroid/location/LocationManager;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->liveLocationListener:Landroid/location/LocationListener;

    invoke-virtual {v0, v1}, Landroid/location/LocationManager;->removeUpdates(Landroid/location/LocationListener;)V
    :try_end_0
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_0

    .line 514
    goto :goto_0

    .line 513
    :catch_0
    move-exception v0

    .line 515
    :goto_0
    return-void
.end method

.method private submitScan(Landroid/location/Location;)V
    .locals 3

    .line 443
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->scanInFlight:Z

    .line 444
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    iput-wide v0, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncAtMs:J

    .line 445
    new-instance v0, Landroid/location/Location;

    invoke-direct {v0, p1}, Landroid/location/Location;-><init>(Landroid/location/Location;)V

    iput-object v0, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncLocation:Landroid/location/Location;

    .line 446
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->refreshActionButtons()V

    .line 447
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->captureLocation(Landroid/location/Location;)V

    .line 448
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->roamCoordsText:Landroid/widget/TextView;

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->formatLocationSummary(Landroid/location/Location;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 449
    const-string v0, "\u0421\u0432\u0435\u0440\u044f\u044e \u043f\u043e\u0437\u0438\u0446\u0438\u044e \u0438 \u043e\u0431\u043d\u043e\u0432\u043b\u044f\u044e \u0431\u043b\u0438\u0436\u0430\u0439\u0448\u0438\u0435 \u0441\u0438\u0433\u043d\u0430\u043b\u044b \u0432\u043e\u043a\u0440\u0443\u0433 \u0442\u0435\u0431\u044f."

    const-string v1, "\u041f\u041e\u0418\u0421\u041a"

    const-string v2, "\u0421\u0438\u043d\u0445\u0440\u043e\u043d\u0438\u0437\u0438\u0440\u0443\u044e \u0441\u0435\u043a\u0442\u043e\u0440\u2026"

    invoke-direct {p0, v2, v0, v1}, Lio/peakmood/mobile/MainActivity;->setSharedStatus(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 455
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lio/peakmood/mobile/MainActivity$6;

    invoke-direct {v1, p0, p1}, Lio/peakmood/mobile/MainActivity$6;-><init>(Lio/peakmood/mobile/MainActivity;Landroid/location/Location;)V

    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    .line 477
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 478
    return-void
.end method

.method private terrainSnapshotFor(DDD)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;
    .locals 7

    .line 853
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->terrainModel:Lio/peakmood/mobile/TerrainModel;

    if-nez v0, :cond_0

    .line 854
    const/4 p1, 0x0

    return-object p1

    .line 856
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->terrainModel:Lio/peakmood/mobile/TerrainModel;

    move-wide v1, p1

    move-wide v3, p3

    move-wide v5, p5

    invoke-virtual/range {v0 .. v6}, Lio/peakmood/mobile/TerrainModel;->snapshot(DDD)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;

    move-result-object p1

    return-object p1
.end method

.method private terrainSnapshotFor(Landroid/location/Location;)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;
    .locals 7

    .line 846
    if-nez p1, :cond_0

    .line 847
    const/4 p1, 0x0

    return-object p1

    .line 849
    :cond_0
    invoke-virtual {p1}, Landroid/location/Location;->getLatitude()D

    move-result-wide v1

    invoke-virtual {p1}, Landroid/location/Location;->getLongitude()D

    move-result-wide v3

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->readAltitude(Landroid/location/Location;)D

    move-result-wide v5

    move-object v0, p0

    invoke-direct/range {v0 .. v6}, Lio/peakmood/mobile/MainActivity;->terrainSnapshotFor(DDD)Lio/peakmood/mobile/TerrainModel$TerrainSnapshot;

    move-result-object p1

    return-object p1
.end method

.method private tierForAltitude(D)Ljava/lang/String;
    .locals 3

    .line 902
    const-wide v0, 0x40c28e0000000000L    # 9500.0

    cmpl-double v2, p1, v0

    if-ltz v2, :cond_0

    .line 903
    const-string p1, "FLAG"

    return-object p1

    .line 905
    :cond_0
    const-wide v0, 0x40b0680000000000L    # 4200.0

    cmpl-double v2, p1, v0

    if-ltz v2, :cond_1

    .line 906
    const-string p1, "epic"

    return-object p1

    .line 908
    :cond_1
    const-wide v0, 0x409c200000000000L    # 1800.0

    cmpl-double v2, p1, v0

    if-ltz v2, :cond_2

    .line 909
    const-string p1, "rare"

    return-object p1

    .line 911
    :cond_2
    const-string p1, "common"

    return-object p1
.end method

.method private tierLabel(Ljava/lang/String;)Ljava/lang/String;
    .locals 1

    .line 882
    const-string v0, "common"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 883
    const-string p1, "\u043e\u0431\u044b\u0447\u043d\u044b\u0439"

    return-object p1

    .line 885
    :cond_0
    const-string v0, "rare"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 886
    const-string p1, "\u0440\u0435\u0434\u043a\u0438\u0439"

    return-object p1

    .line 888
    :cond_1
    const-string v0, "epic"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    .line 889
    const-string p1, "\u044d\u043f\u0438\u0447\u0435\u0441\u043a\u0438\u0439"

    return-object p1

    .line 891
    :cond_2
    const-string v0, "FLAG"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    .line 892
    const-string p1, "\u043c\u0438\u0444\u0438\u0447\u0435\u0441\u043a\u0438\u0439"

    return-object p1

    .line 894
    :cond_3
    const-string p1, "\u0421\u043a\u0430\u043d\u0438\u0440\u0443\u0435\u043c..."

    return-object p1
.end method

.method private tierLabelUpper(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    .line 898
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->tierLabel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    new-instance v0, Ljava/util/Locale;

    const-string v1, "ru"

    invoke-direct {v0, v1}, Ljava/util/Locale;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, v0}, Ljava/lang/String;->toUpperCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object p1

    return-object p1
.end method

.method private triggerGeoSync(Landroid/location/Location;Z)V
    .locals 9

    .line 383
    if-nez p1, :cond_0

    .line 384
    return-void

    .line 386
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->sessionToken:Ljava/lang/String;

    if-nez v0, :cond_1

    .line 387
    invoke-direct {p0, p2}, Lio/peakmood/mobile/MainActivity;->ensureSessionConnected(Z)V

    .line 388
    return-void

    .line 390
    :cond_1
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-nez v0, :cond_a

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->hitInFlight:Z

    if-nez v0, :cond_a

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->openInFlight:Z

    if-eqz v0, :cond_2

    goto :goto_3

    .line 393
    :cond_2
    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->scanInFlight:Z

    if-nez v0, :cond_9

    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->sessionInFlight:Z

    if-eqz v0, :cond_3

    goto :goto_2

    .line 396
    :cond_3
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 397
    if-nez p2, :cond_8

    .line 398
    iget-object p2, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncLocation:Landroid/location/Location;

    if-eqz p2, :cond_7

    .line 399
    iget-object p2, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncLocation:Landroid/location/Location;

    invoke-virtual {p1, p2}, Landroid/location/Location;->distanceTo(Landroid/location/Location;)F

    move-result p2

    .line 400
    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->readAltitude(Landroid/location/Location;)D

    move-result-wide v2

    invoke-static {v2, v3}, Ljava/lang/Math;->abs(D)D

    move-result-wide v2

    iget-object v4, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncLocation:Landroid/location/Location;

    invoke-direct {p0, v4}, Lio/peakmood/mobile/MainActivity;->readAltitude(Landroid/location/Location;)D

    move-result-wide v4

    invoke-static {v4, v5}, Ljava/lang/Math;->abs(D)D

    move-result-wide v4

    sub-double/2addr v2, v4

    invoke-static {v2, v3}, Ljava/lang/Math;->abs(D)D

    move-result-wide v2

    .line 401
    const/high16 v4, 0x41f00000    # 30.0f

    const/4 v5, 0x0

    const/4 v6, 0x1

    cmpl-float p2, p2, v4

    if-gez p2, :cond_5

    const-wide/high16 v7, 0x4032000000000000L    # 18.0

    cmpl-double p2, v2, v7

    if-ltz p2, :cond_4

    goto :goto_0

    :cond_4
    const/4 p2, 0x0

    goto :goto_1

    :cond_5
    :goto_0
    const/4 p2, 0x1

    .line 402
    :goto_1
    iget-wide v2, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncAtMs:J

    sub-long v2, v0, v2

    const-wide/16 v7, 0x3a98

    cmp-long v4, v2, v7

    if-ltz v4, :cond_6

    const/4 v5, 0x1

    .line 403
    :cond_6
    if-nez p2, :cond_7

    if-nez v5, :cond_7

    .line 404
    return-void

    .line 407
    :cond_7
    iget-wide v2, p0, Lio/peakmood/mobile/MainActivity;->lastGeoSyncAtMs:J

    sub-long/2addr v0, v2

    const-wide/16 v2, 0xfa0

    cmp-long p2, v0, v2

    if-gez p2, :cond_8

    .line 408
    return-void

    .line 411
    :cond_8
    new-instance p2, Landroid/location/Location;

    invoke-direct {p2, p1}, Landroid/location/Location;-><init>(Landroid/location/Location;)V

    invoke-direct {p0, p2}, Lio/peakmood/mobile/MainActivity;->submitScan(Landroid/location/Location;)V

    .line 412
    return-void

    .line 394
    :cond_9
    :goto_2
    return-void

    .line 391
    :cond_a
    :goto_3
    return-void
.end method

.method private updateCameraPreview()V
    .locals 1

    .line 291
    iget-boolean v0, p0, Lio/peakmood/mobile/MainActivity;->encounterVisible:Z

    if-eqz v0, :cond_0

    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->hasCameraPermission()Z

    move-result v0

    if-eqz v0, :cond_0

    .line 292
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->cameraPreviewView:Lio/peakmood/mobile/CameraPreviewView;

    invoke-virtual {v0}, Lio/peakmood/mobile/CameraPreviewView;->startPreview()V

    .line 293
    return-void

    .line 295
    :cond_0
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->cameraPreviewView:Lio/peakmood/mobile/CameraPreviewView;

    invoke-virtual {v0}, Lio/peakmood/mobile/CameraPreviewView;->stopPreview()V

    .line 296
    return-void
.end method

.method private updateMiningScene()V
    .locals 6

    .line 261
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->miningSceneView:Lio/peakmood/mobile/MiningSceneView;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    const/4 v2, 0x0

    if-eqz v1, :cond_0

    const/4 v1, 0x1

    goto :goto_0

    :cond_0
    const/4 v1, 0x0

    :goto_0
    iget-object v3, p0, Lio/peakmood/mobile/MainActivity;->currentTier:Ljava/lang/String;

    iget v4, p0, Lio/peakmood/mobile/MainActivity;->currentHitsLeft:I

    iget v5, p0, Lio/peakmood/mobile/MainActivity;->currentNodeHp:I

    invoke-virtual {v0, v1, v3, v4, v5}, Lio/peakmood/mobile/MiningSceneView;->setNodeState(ZLjava/lang/String;II)V

    .line 262
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->nodeTitleText:Landroid/widget/TextView;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-nez v1, :cond_1

    const/16 v2, 0x8

    :cond_1
    invoke-virtual {v0, v2}, Landroid/widget/TextView;->setVisibility(I)V

    .line 263
    return-void
.end method

.method private updateResumeEncounterButton()V
    .locals 2

    .line 222
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->resumeEncounterButton:Landroid/widget/Button;

    iget-object v1, p0, Lio/peakmood/mobile/MainActivity;->currentNodeId:Ljava/lang/String;

    if-nez v1, :cond_0

    const/16 v1, 0x8

    goto :goto_0

    :cond_0
    const/4 v1, 0x0

    :goto_0
    invoke-virtual {v0, v1}, Landroid/widget/Button;->setVisibility(I)V

    .line 223
    return-void
.end method


# virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 0

    .line 108
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 109
    const/high16 p1, 0x7f030000

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/MainActivity;->setContentView(I)V

    .line 111
    const-string p1, "location"

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Landroid/location/LocationManager;

    iput-object p1, p0, Lio/peakmood/mobile/MainActivity;->locationManager:Landroid/location/LocationManager;

    .line 112
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->loadOrCreateDeviceId()Ljava/lang/String;

    move-result-object p1

    iput-object p1, p0, Lio/peakmood/mobile/MainActivity;->deviceId:Ljava/lang/String;

    .line 113
    invoke-static {p0}, Lio/peakmood/mobile/TerrainModel;->getInstance(Landroid/content/Context;)Lio/peakmood/mobile/TerrainModel;

    move-result-object p1

    iput-object p1, p0, Lio/peakmood/mobile/MainActivity;->terrainModel:Lio/peakmood/mobile/TerrainModel;

    .line 115
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->bindViews()V

    .line 116
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->configureMapViews()V

    .line 117
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->configureButtons()V

    .line 119
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->resetNodeUi()V

    .line 120
    const p1, 0x7f06000e

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->setLootText(Ljava/lang/String;)V

    .line 121
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->showRoamMode()V

    .line 122
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->ensureLocationBootstrap()V

    .line 123
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->ensureCameraPermission()V

    .line 124
    return-void
.end method

.method protected onPause()V
    .locals 1

    .line 136
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->stopLiveLocationUpdates()V

    .line 137
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity;->cameraPreviewView:Lio/peakmood/mobile/CameraPreviewView;

    invoke-virtual {v0}, Lio/peakmood/mobile/CameraPreviewView;->stopPreview()V

    .line 138
    invoke-super {p0}, Landroid/app/Activity;->onPause()V

    .line 139
    return-void
.end method

.method public onRequestPermissionsResult(I[Ljava/lang/String;[I)V
    .locals 3

    .line 945
    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;->onRequestPermissionsResult(I[Ljava/lang/String;[I)V

    .line 946
    const/16 p2, 0x2a

    const/4 v0, 0x1

    const/4 v1, 0x0

    if-ne p1, p2, :cond_3

    .line 947
    nop

    .line 948
    array-length p1, p3

    const/4 p2, 0x0

    :goto_0
    if-ge p2, p1, :cond_1

    aget v2, p3, p2

    .line 949
    if-nez v2, :cond_0

    .line 950
    nop

    .line 951
    goto :goto_1

    .line 948
    :cond_0
    add-int/lit8 p2, p2, 0x1

    goto :goto_0

    :cond_1
    const/4 v0, 0x0

    .line 954
    :goto_1
    if-eqz v0, :cond_2

    .line 955
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->ensureLocationBootstrap()V

    goto :goto_2

    .line 957
    :cond_2
    const p1, 0x7f060014

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->showError(Ljava/lang/String;)V

    .line 959
    :goto_2
    return-void

    .line 962
    :cond_3
    const/16 p2, 0x2b

    if-ne p1, p2, :cond_7

    .line 963
    nop

    .line 964
    array-length p1, p3

    const/4 p2, 0x0

    :goto_3
    if-ge p2, p1, :cond_5

    aget v2, p3, p2

    .line 965
    if-nez v2, :cond_4

    .line 966
    nop

    .line 967
    goto :goto_4

    .line 964
    :cond_4
    add-int/lit8 p2, p2, 0x1

    goto :goto_3

    :cond_5
    const/4 v0, 0x0

    .line 970
    :goto_4
    if-eqz v0, :cond_6

    .line 971
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateCameraPreview()V

    goto :goto_5

    .line 973
    :cond_6
    const p1, 0x7f060017

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->showError(Ljava/lang/String;)V

    .line 974
    const p1, 0x7f060018

    invoke-virtual {p0, p1}, Lio/peakmood/mobile/MainActivity;->getString(I)Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Lio/peakmood/mobile/MainActivity;->setLootText(Ljava/lang/String;)V

    .line 977
    :cond_7
    :goto_5
    return-void
.end method

.method protected onResume()V
    .locals 0

    .line 128
    invoke-super {p0}, Landroid/app/Activity;->onResume()V

    .line 129
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->updateCameraPreview()V

    .line 130
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->startLiveLocationUpdates()V

    .line 131
    invoke-direct {p0}, Lio/peakmood/mobile/MainActivity;->ensureLocationBootstrap()V

    .line 132
    return-void
.end method
