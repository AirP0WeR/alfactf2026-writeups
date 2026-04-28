.class public Lio/peakmood/mobile/WorldMapView;
.super Landroid/view/View;
.source "WorldMapView.java"


# static fields
.field private static final IN_FLIGHT:Ljava/util/Set;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Set<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private static final MAX_MEMORY_TILES:I = 0x80

.field private static final MAX_TILE_ZOOM:I = 0x11

.field private static final MEMORY_CACHE:Ljava/util/Map;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Landroid/graphics/Bitmap;",
            ">;"
        }
    .end annotation
.end field

.field private static final TAG:Ljava/lang/String; = "WorldMapView"

.field private static final TILE_EXECUTOR:Ljava/util/concurrent/ExecutorService;

.field private static final TILE_HOSTS:[Ljava/lang/String;

.field private static final TILE_SCHEMES:[Ljava/lang/String;

.field private static final TILE_SIZE:I = 0x100

.field private static final TILE_TEMPLATE:Ljava/lang/String; = "%s://%s/%d/%d/%d.png"

.field public static final VIEWPORT_AUTO:I = 0x0

.field public static final VIEWPORT_EXPANDED:I = 0x1

.field public static final VIEWPORT_PANEL:I = 0x2


# instance fields
.field private final attributionPaint:Landroid/graphics/Paint;

.field private final captionPaint:Landroid/graphics/Paint;

.field private final diskCacheDir:Ljava/io/File;

.field private hasLocation:Z

.field private hitsLeft:I

.field private hpTotal:I

.field private nodeActive:Z

.field private final nodeCorePaint:Landroid/graphics/Paint;

.field private nodeId:Ljava/lang/String;

.field private nodeLat:D

.field private nodeLon:D

.field private final nodePaint:Landroid/graphics/Paint;

.field private final nodePulsePaint:Landroid/graphics/Paint;

.field private final nodeRingPaint:Landroid/graphics/Paint;

.field private final nodeTrailPaint:Landroid/graphics/Paint;

.field private playerAlt:D

.field private final playerHaloPaint:Landroid/graphics/Paint;

.field private playerLat:D

.field private playerLon:D

.field private final playerPaint:Landroid/graphics/Paint;

.field private final ringPaint:Landroid/graphics/Paint;

.field private final ripplePaint:Landroid/graphics/Paint;

.field private final scopeClipPath:Landroid/graphics/Path;

.field private final scopeFillPaint:Landroid/graphics/Paint;

.field private final sweepEdgePaint:Landroid/graphics/Paint;

.field private final sweepFillPaint:Landroid/graphics/Paint;

.field private final tickPaint:Landroid/graphics/Paint;

.field private tier:Ljava/lang/String;

.field private final tileGridPaint:Landroid/graphics/Paint;

.field private final tilePlaceholderPaint:Landroid/graphics/Paint;

.field private final tileTintPaint:Landroid/graphics/Paint;

.field private viewportMode:I

.field private final workingRect:Landroid/graphics/RectF;

.field private zoomLevelOverride:I


# direct methods
.method static constructor <clinit>()V
    .locals 7

    .line 38
    const/4 v0, 0x4

    invoke-static {v0}, Ljava/util/concurrent/Executors;->newFixedThreadPool(I)Ljava/util/concurrent/ExecutorService;

    move-result-object v1

    sput-object v1, Lio/peakmood/mobile/WorldMapView;->TILE_EXECUTOR:Ljava/util/concurrent/ExecutorService;

    .line 39
    new-instance v1, Lio/peakmood/mobile/WorldMapView$1;

    const/16 v2, 0x80

    const/high16 v3, 0x3f400000    # 0.75f

    const/4 v4, 0x1

    invoke-direct {v1, v2, v3, v4}, Lio/peakmood/mobile/WorldMapView$1;-><init>(IFZ)V

    invoke-static {v1}, Ljava/util/Collections;->synchronizedMap(Ljava/util/Map;)Ljava/util/Map;

    move-result-object v1

    sput-object v1, Lio/peakmood/mobile/WorldMapView;->MEMORY_CACHE:Ljava/util/Map;

    .line 47
    new-instance v1, Ljava/util/concurrent/ConcurrentHashMap;

    invoke-direct {v1}, Ljava/util/concurrent/ConcurrentHashMap;-><init>()V

    invoke-static {v1}, Ljava/util/Collections;->newSetFromMap(Ljava/util/Map;)Ljava/util/Set;

    move-result-object v1

    sput-object v1, Lio/peakmood/mobile/WorldMapView;->IN_FLIGHT:Ljava/util/Set;

    .line 48
    const/16 v1, 0xc

    new-array v1, v1, [Ljava/lang/String;

    const/4 v2, 0x0

    const-string v3, "a-tile-opentopomap.alfactf.ru"

    aput-object v3, v1, v2

    const-string v3, "b-tile-opentopomap.alfactf.ru"

    aput-object v3, v1, v4

    const/4 v3, 0x2

    const-string v5, "c-tile-opentopomap.alfactf.ru"

    aput-object v5, v1, v3

    const-string v5, "a2-tile-opentopomap.alfactf.ru"

    const/4 v6, 0x3

    aput-object v5, v1, v6

    const-string v5, "b2-tile-opentopomap.alfactf.ru"

    aput-object v5, v1, v0

    const-string v0, "c2-tile-opentopomap.alfactf.ru"

    const/4 v5, 0x5

    aput-object v0, v1, v5

    const-string v0, "a3-tile-opentopomap.alfactf.ru"

    const/4 v5, 0x6

    aput-object v0, v1, v5

    const-string v0, "b3-tile-opentopomap.alfactf.ru"

    const/4 v5, 0x7

    aput-object v0, v1, v5

    const-string v0, "c3-tile-opentopomap.alfactf.ru"

    const/16 v5, 0x8

    aput-object v0, v1, v5

    const-string v0, "a4-tile-opentopomap.alfactf.ru"

    const/16 v5, 0x9

    aput-object v0, v1, v5

    const-string v0, "b4-tile-opentopomap.alfactf.ru"

    const/16 v5, 0xa

    aput-object v0, v1, v5

    const-string v0, "c4-tile-opentopomap.alfactf.ru"

    const/16 v5, 0xb

    aput-object v0, v1, v5

    sput-object v1, Lio/peakmood/mobile/WorldMapView;->TILE_HOSTS:[Ljava/lang/String;

    .line 62
    new-array v0, v3, [Ljava/lang/String;

    const-string v1, "https"

    aput-object v1, v0, v2

    const-string v1, "http"

    aput-object v1, v0, v4

    sput-object v0, Lio/peakmood/mobile/WorldMapView;->TILE_SCHEMES:[Ljava/lang/String;

    return-void
.end method

.method public constructor <init>(Landroid/content/Context;)V
    .locals 1

    .line 102
    const/4 v0, 0x0

    invoke-direct {p0, p1, v0}, Lio/peakmood/mobile/WorldMapView;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;)V

    .line 103
    return-void
.end method

.method public constructor <init>(Landroid/content/Context;Landroid/util/AttributeSet;)V
    .locals 3

    .line 106
    invoke-direct {p0, p1, p2}, Landroid/view/View;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;)V

    .line 65
    new-instance p2, Landroid/graphics/Paint;

    const/4 v0, 0x1

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tilePlaceholderPaint:Landroid/graphics/Paint;

    .line 66
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    .line 67
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileTintPaint:Landroid/graphics/Paint;

    .line 68
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    .line 69
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    .line 70
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    .line 71
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    .line 72
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    .line 73
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ripplePaint:Landroid/graphics/Paint;

    .line 74
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerPaint:Landroid/graphics/Paint;

    .line 75
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerHaloPaint:Landroid/graphics/Paint;

    .line 76
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodePaint:Landroid/graphics/Paint;

    .line 77
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeCorePaint:Landroid/graphics/Paint;

    .line 78
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    .line 79
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    .line 80
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodePulsePaint:Landroid/graphics/Paint;

    .line 81
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    .line 82
    new-instance p2, Landroid/graphics/Paint;

    invoke-direct {p2, v0}, Landroid/graphics/Paint;-><init>(I)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->attributionPaint:Landroid/graphics/Paint;

    .line 83
    new-instance p2, Landroid/graphics/RectF;

    invoke-direct {p2}, Landroid/graphics/RectF;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    .line 84
    new-instance p2, Landroid/graphics/Path;

    invoke-direct {p2}, Landroid/graphics/Path;-><init>()V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    .line 87
    const/4 p2, 0x0

    iput-boolean p2, p0, Lio/peakmood/mobile/WorldMapView;->hasLocation:Z

    .line 88
    iput-boolean p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeActive:Z

    .line 92
    const-wide/high16 v0, 0x7ff8000000000000L    # Double.NaN

    iput-wide v0, p0, Lio/peakmood/mobile/WorldMapView;->nodeLat:D

    .line 93
    iput-wide v0, p0, Lio/peakmood/mobile/WorldMapView;->nodeLon:D

    .line 94
    const-string v0, ""

    iput-object v0, p0, Lio/peakmood/mobile/WorldMapView;->nodeId:Ljava/lang/String;

    .line 95
    const-string v0, "none"

    iput-object v0, p0, Lio/peakmood/mobile/WorldMapView;->tier:Ljava/lang/String;

    .line 96
    iput p2, p0, Lio/peakmood/mobile/WorldMapView;->hitsLeft:I

    .line 97
    iput p2, p0, Lio/peakmood/mobile/WorldMapView;->hpTotal:I

    .line 98
    iput p2, p0, Lio/peakmood/mobile/WorldMapView;->viewportMode:I

    .line 99
    const/4 p2, -0x1

    iput p2, p0, Lio/peakmood/mobile/WorldMapView;->zoomLevelOverride:I

    .line 108
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tilePlaceholderPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 109
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tilePlaceholderPaint:Landroid/graphics/Paint;

    const v0, 0x7f05000c

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setColor(I)V

    .line 111
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 112
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    const/high16 v0, 0x3f800000    # 1.0f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 113
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    const v1, 0x7f05000d

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 114
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    const/16 v2, 0x5a

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 116
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileTintPaint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 117
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tileTintPaint:Landroid/graphics/Paint;

    const v2, 0x1807141a

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 119
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 120
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const v2, 0x3fb33333    # 1.4f

    invoke-direct {p0, v2}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 121
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const v2, 0x7f05000b

    invoke-direct {p0, v2}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 123
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 124
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    const v2, 0x30091318

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 126
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 127
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 128
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setColor(I)V

    .line 129
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    const/16 v0, 0x78

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 131
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 132
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    const v0, 0x2a9ef2de

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setColor(I)V

    .line 134
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 135
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Cap;->ROUND:Landroid/graphics/Paint$Cap;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStrokeCap(Landroid/graphics/Paint$Cap;)V

    .line 136
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const v0, 0x400ccccd    # 2.2f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 137
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const v1, 0x7f050005

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 138
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const/16 v2, 0xd2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 140
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ripplePaint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 141
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ripplePaint:Landroid/graphics/Paint;

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 142
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->ripplePaint:Landroid/graphics/Paint;

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setColor(I)V

    .line 144
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 145
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerPaint:Landroid/graphics/Paint;

    const v0, 0x7f05000f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setColor(I)V

    .line 147
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerHaloPaint:Landroid/graphics/Paint;

    sget-object v2, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 148
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerHaloPaint:Landroid/graphics/Paint;

    const v2, 0x40266666    # 2.6f

    invoke-direct {p0, v2}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v2

    invoke-virtual {p2, v2}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 149
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->playerHaloPaint:Landroid/graphics/Paint;

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 151
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodePaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 153
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeCorePaint:Landroid/graphics/Paint;

    sget-object v1, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 154
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeCorePaint:Landroid/graphics/Paint;

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setColor(I)V

    .line 156
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 157
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    const v0, 0x4019999a    # 2.4f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 159
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->STROKE:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 160
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Cap;->ROUND:Landroid/graphics/Paint$Cap;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStrokeCap(Landroid/graphics/Paint$Cap;)V

    .line 161
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    const v0, 0x40333333    # 2.8f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 163
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodePulsePaint:Landroid/graphics/Paint;

    sget-object v0, Landroid/graphics/Paint$Style;->FILL:Landroid/graphics/Paint$Style;

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setStyle(Landroid/graphics/Paint$Style;)V

    .line 165
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    const v0, 0x7f050004

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setColor(I)V

    .line 166
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    const/high16 v1, 0x41280000    # 10.5f

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v1

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 167
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    const v1, 0x3da3d70a    # 0.08f

    invoke-virtual {p2, v1}, Landroid/graphics/Paint;->setLetterSpacing(F)V

    .line 169
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->attributionPaint:Landroid/graphics/Paint;

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setColor(I)V

    .line 170
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->attributionPaint:Landroid/graphics/Paint;

    const/high16 v0, 0x41100000    # 9.0f

    invoke-direct {p0, v0}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v0

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setTextSize(F)V

    .line 171
    iget-object p2, p0, Lio/peakmood/mobile/WorldMapView;->attributionPaint:Landroid/graphics/Paint;

    const/16 v0, 0xb9

    invoke-virtual {p2, v0}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 173
    new-instance p2, Ljava/io/File;

    invoke-virtual {p1}, Landroid/content/Context;->getCacheDir()Ljava/io/File;

    move-result-object p1

    const-string v0, "opentopomap-tiles"

    invoke-direct {p2, p1, v0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->diskCacheDir:Ljava/io/File;

    .line 174
    iget-object p1, p0, Lio/peakmood/mobile/WorldMapView;->diskCacheDir:Ljava/io/File;

    invoke-virtual {p1}, Ljava/io/File;->exists()Z

    move-result p1

    if-nez p1, :cond_0

    .line 176
    iget-object p1, p0, Lio/peakmood/mobile/WorldMapView;->diskCacheDir:Ljava/io/File;

    invoke-virtual {p1}, Ljava/io/File;->mkdirs()Z

    .line 178
    :cond_0
    return-void
.end method

.method static synthetic access$000(Lio/peakmood/mobile/WorldMapView;IIILjava/io/File;)V
    .locals 0
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 29
    invoke-direct {p0, p1, p2, p3, p4}, Lio/peakmood/mobile/WorldMapView;->downloadTile(IIILjava/io/File;)V

    return-void
.end method

.method static synthetic access$100()Ljava/util/Map;
    .locals 1

    .line 29
    sget-object v0, Lio/peakmood/mobile/WorldMapView;->MEMORY_CACHE:Ljava/util/Map;

    return-object v0
.end method

.method static synthetic access$200()Ljava/util/Set;
    .locals 1

    .line 29
    sget-object v0, Lio/peakmood/mobile/WorldMapView;->IN_FLIGHT:Ljava/util/Set;

    return-object v0
.end method

.method private clamp(FFF)F
    .locals 0

    .line 606
    invoke-static {p3, p1}, Ljava/lang/Math;->min(FF)F

    move-result p1

    invoke-static {p2, p1}, Ljava/lang/Math;->max(FF)F

    move-result p1

    return p1
.end method

.method private distanceMeters(DDDD)D
    .locals 4

    .line 626
    nop

    .line 627
    invoke-static {p1, p2}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide v0

    .line 628
    invoke-static {p5, p6}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide v2

    .line 629
    sub-double/2addr p5, p1

    invoke-static {p5, p6}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide p1

    .line 630
    sub-double/2addr p7, p3

    invoke-static {p7, p8}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide p3

    .line 631
    const-wide/high16 p5, 0x4000000000000000L    # 2.0

    div-double/2addr p1, p5

    invoke-static {p1, p2}, Ljava/lang/Math;->sin(D)D

    move-result-wide p7

    invoke-static {p1, p2}, Ljava/lang/Math;->sin(D)D

    move-result-wide p1

    mul-double p7, p7, p1

    .line 632
    invoke-static {v0, v1}, Ljava/lang/Math;->cos(D)D

    move-result-wide p1

    invoke-static {v2, v3}, Ljava/lang/Math;->cos(D)D

    move-result-wide v0

    mul-double p1, p1, v0

    div-double/2addr p3, p5

    invoke-static {p3, p4}, Ljava/lang/Math;->sin(D)D

    move-result-wide p5

    mul-double p1, p1, p5

    invoke-static {p3, p4}, Ljava/lang/Math;->sin(D)D

    move-result-wide p3

    mul-double p1, p1, p3

    add-double/2addr p7, p1

    .line 633
    invoke-static {p7, p8}, Ljava/lang/Math;->sqrt(D)D

    move-result-wide p1

    const-wide/high16 p3, 0x3ff0000000000000L    # 1.0

    sub-double/2addr p3, p7

    invoke-static {p3, p4}, Ljava/lang/Math;->sqrt(D)D

    move-result-wide p3

    invoke-static {p1, p2, p3, p4}, Ljava/lang/Math;->atan2(DD)D

    move-result-wide p1

    const-wide p3, 0x41684dae00000000L    # 1.2742E7

    mul-double p3, p3, p1

    return-wide p3
.end method

.method private downloadTile(IIILjava/io/File;)V
    .locals 11
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 513
    sget-object v0, Lio/peakmood/mobile/WorldMapView;->TILE_HOSTS:[Ljava/lang/String;

    add-int v1, p2, p3

    sget-object v2, Lio/peakmood/mobile/WorldMapView;->TILE_HOSTS:[Ljava/lang/String;

    array-length v2, v2

    invoke-static {v1, v2}, Lio/peakmood/mobile/WorldMapView$$ExternalSyntheticBackport0;->m(II)I

    move-result v1

    aget-object v4, v0, v1

    .line 514
    nop

    .line 515
    sget-object v1, Lio/peakmood/mobile/WorldMapView;->TILE_SCHEMES:[Ljava/lang/String;

    array-length v9, v1

    const/4 v0, 0x0

    const/4 v2, 0x0

    const/4 v10, 0x0

    :goto_0
    if-ge v10, v9, :cond_0

    aget-object v3, v1, v10

    .line 517
    move-object v2, p0

    move v5, p1

    move v6, p2

    move v7, p3

    move-object v8, p4

    :try_start_0
    invoke-direct/range {v2 .. v8}, Lio/peakmood/mobile/WorldMapView;->downloadTileWithScheme(Ljava/lang/String;Ljava/lang/String;IIILjava/io/File;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 518
    return-void

    .line 519
    :catch_0
    move-exception v0

    .line 520
    nop

    .line 521
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "Tile fetch via "

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string p2, " failed for "

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string p2, "/"

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v5}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v7}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    const-string p2, "WorldMapView"

    invoke-static {p2, p1, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 515
    add-int/lit8 v10, v10, 0x1

    move p1, v5

    move p2, v6

    move p3, v7

    move-object p4, v8

    goto :goto_0

    .line 525
    :cond_0
    if-nez v0, :cond_1

    new-instance v0, Ljava/io/IOException;

    const-string p1, "Tile fetch failed without exception"

    invoke-direct {v0, p1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    :cond_1
    goto :goto_2

    :goto_1
    throw v0

    :goto_2
    goto :goto_1
.end method

.method private downloadTileWithScheme(Ljava/lang/String;Ljava/lang/String;IIILjava/io/File;)V
    .locals 4
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 529
    new-instance v0, Ljava/net/URL;

    sget-object v1, Ljava/util/Locale;->US:Ljava/util/Locale;

    invoke-static {p3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object p3

    invoke-static {p4}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object p4

    invoke-static {p5}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object p5

    const/4 v2, 0x5

    new-array v2, v2, [Ljava/lang/Object;

    const/4 v3, 0x0

    aput-object p1, v2, v3

    const/4 p1, 0x1

    aput-object p2, v2, p1

    const/4 p2, 0x2

    aput-object p3, v2, p2

    const/4 p2, 0x3

    aput-object p4, v2, p2

    const/4 p2, 0x4

    aput-object p5, v2, p2

    const-string p2, "%s://%s/%d/%d/%d.png"

    invoke-static {v1, p2, v2}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p2

    invoke-direct {v0, p2}, Ljava/net/URL;-><init>(Ljava/lang/String;)V

    .line 530
    invoke-virtual {v0}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;

    move-result-object p2

    check-cast p2, Ljava/net/HttpURLConnection;

    .line 531
    const/16 p3, 0x1770

    invoke-virtual {p2, p3}, Ljava/net/HttpURLConnection;->setConnectTimeout(I)V

    .line 532
    invoke-virtual {p2, p3}, Ljava/net/HttpURLConnection;->setReadTimeout(I)V

    .line 533
    invoke-virtual {p2, p1}, Ljava/net/HttpURLConnection;->setUseCaches(Z)V

    .line 534
    const-string p1, "Accept"

    const-string p3, "image/png"

    invoke-virtual {p2, p1, p3}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    .line 535
    const-string p1, "User-Agent"

    const-string p3, "PeakMood/1.0 (Android)"

    invoke-virtual {p2, p1, p3}, Ljava/net/HttpURLConnection;->setRequestProperty(Ljava/lang/String;Ljava/lang/String;)V

    .line 538
    :try_start_0
    invoke-virtual {p2}, Ljava/net/HttpURLConnection;->getResponseCode()I

    move-result p1

    .line 539
    const/16 p3, 0xc8

    if-ne p1, p3, :cond_3

    .line 543
    invoke-virtual {p2}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object p1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_4

    :try_start_1
    new-instance p3, Ljava/io/FileOutputStream;

    invoke-direct {p3, p6}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_2

    .line 544
    const/16 p4, 0x2000

    :try_start_2
    new-array p4, p4, [B

    .line 546
    :goto_0
    invoke-virtual {p1, p4}, Ljava/io/InputStream;->read([B)I

    move-result p5

    const/4 p6, -0x1

    if-eq p5, p6, :cond_0

    .line 547
    invoke-virtual {p3, p4, v3, p5}, Ljava/io/FileOutputStream;->write([BII)V

    goto :goto_0

    .line 549
    :cond_0
    invoke-virtual {p3}, Ljava/io/FileOutputStream;->flush()V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 550
    :try_start_3
    invoke-virtual {p3}, Ljava/io/FileOutputStream;->close()V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_2

    if-eqz p1, :cond_1

    :try_start_4
    invoke-virtual {p1}, Ljava/io/InputStream;->close()V
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_4

    .line 552
    :cond_1
    invoke-virtual {p2}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 553
    nop

    .line 554
    return-void

    .line 543
    :catchall_0
    move-exception p4

    :try_start_5
    invoke-virtual {p3}, Ljava/io/FileOutputStream;->close()V
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_1

    goto :goto_1

    :catchall_1
    move-exception p3

    :try_start_6
    invoke-static {p4, p3}, Lio/peakmood/mobile/MainActivity$$ExternalSyntheticBackport0;->m(Ljava/lang/Throwable;Ljava/lang/Throwable;)V

    :goto_1
    throw p4
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_2

    :catchall_2
    move-exception p3

    if-eqz p1, :cond_2

    :try_start_7
    invoke-virtual {p1}, Ljava/io/InputStream;->close()V
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_3

    goto :goto_2

    :catchall_3
    move-exception p1

    :try_start_8
    invoke-static {p3, p1}, Lio/peakmood/mobile/MainActivity$$ExternalSyntheticBackport0;->m(Ljava/lang/Throwable;Ljava/lang/Throwable;)V

    :cond_2
    :goto_2
    throw p3

    .line 540
    :cond_3
    new-instance p3, Ljava/io/IOException;

    new-instance p4, Ljava/lang/StringBuilder;

    invoke-direct {p4}, Ljava/lang/StringBuilder;-><init>()V

    const-string p5, "Unexpected HTTP "

    invoke-virtual {p4, p5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p4

    invoke-virtual {p4, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string p4, " for "

    invoke-virtual {p1, p4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p3, p1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw p3
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_4

    .line 552
    :catchall_4
    move-exception p1

    invoke-virtual {p2}, Ljava/net/HttpURLConnection;->disconnect()V

    .line 553
    goto :goto_4

    :goto_3
    throw p1

    :goto_4
    goto :goto_3
.end method

.method private dp(F)F
    .locals 1

    .line 657
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v0

    iget v0, v0, Landroid/util/DisplayMetrics;->density:F

    mul-float p1, p1, v0

    return p1
.end method

.method private drawAttribution(Landroid/graphics/Canvas;FF)V
    .locals 2

    .line 461
    nop

    .line 462
    invoke-direct {p0, p2, p3}, Lio/peakmood/mobile/WorldMapView;->isCompactMap(FF)Z

    move-result p2

    if-eqz p2, :cond_0

    const/high16 p2, 0x41d00000    # 26.0f

    goto :goto_0

    :cond_0
    const/high16 p2, 0x43240000    # 164.0f

    :goto_0
    invoke-direct {p0, p2}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result p2

    sub-float/2addr p3, p2

    .line 463
    const/high16 p2, 0x41400000    # 12.0f

    invoke-direct {p0, p2}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result p2

    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView;->attributionPaint:Landroid/graphics/Paint;

    const-string v1, "\u0414\u0430\u043d\u043d\u044b\u0435 \u043a\u0430\u0440\u0442\u044b \u00a9 OpenTopoMap, OpenStreetMap"

    invoke-virtual {p1, v1, p2, p3, v0}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 464
    return-void
.end method

.method private drawCaption(Landroid/graphics/Canvas;FF)V
    .locals 17

    .line 438
    move-object/from16 v0, p0

    move-object/from16 v9, p1

    move/from16 v10, p2

    move/from16 v11, p3

    iget-boolean v1, v0, Lio/peakmood/mobile/WorldMapView;->nodeActive:Z

    const/4 v12, 0x1

    const/4 v13, 0x0

    const/4 v14, 0x2

    if-eqz v1, :cond_0

    iget-wide v1, v0, Lio/peakmood/mobile/WorldMapView;->nodeLat:D

    invoke-static {v1, v2}, Ljava/lang/Double;->isNaN(D)Z

    move-result v1

    if-nez v1, :cond_0

    iget-wide v1, v0, Lio/peakmood/mobile/WorldMapView;->nodeLon:D

    invoke-static {v1, v2}, Ljava/lang/Double;->isNaN(D)Z

    move-result v1

    if-nez v1, :cond_0

    .line 439
    sget-object v15, Ljava/util/Locale;->US:Ljava/util/Locale;

    iget-object v1, v0, Lio/peakmood/mobile/WorldMapView;->tier:Ljava/lang/String;

    invoke-direct {v0, v1}, Lio/peakmood/mobile/WorldMapView;->tierLabel(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v16

    iget-wide v1, v0, Lio/peakmood/mobile/WorldMapView;->playerLat:D

    iget-wide v3, v0, Lio/peakmood/mobile/WorldMapView;->playerLon:D

    iget-wide v5, v0, Lio/peakmood/mobile/WorldMapView;->nodeLat:D

    iget-wide v7, v0, Lio/peakmood/mobile/WorldMapView;->nodeLon:D

    invoke-direct/range {v0 .. v8}, Lio/peakmood/mobile/WorldMapView;->distanceMeters(DDDD)D

    move-result-wide v1

    invoke-static {v1, v2}, Ljava/lang/Math;->round(D)J

    move-result-wide v1

    invoke-static {v1, v2}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v1

    new-array v2, v14, [Ljava/lang/Object;

    aput-object v16, v2, v13

    aput-object v1, v2, v12

    const-string v1, "%s \u00b7 %d \u043c"

    invoke-static {v15, v1, v2}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    goto :goto_2

    .line 441
    :cond_0
    sget-object v1, Ljava/util/Locale;->US:Ljava/util/Locale;

    .line 444
    iget-wide v2, v0, Lio/peakmood/mobile/WorldMapView;->playerLat:D

    const-wide/16 v4, 0x0

    cmpl-double v6, v2, v4

    if-ltz v6, :cond_1

    const-string v2, "\u0421"

    goto :goto_0

    :cond_1
    const-string v2, "\u042e"

    :goto_0
    iget-wide v6, v0, Lio/peakmood/mobile/WorldMapView;->playerLat:D

    .line 445
    invoke-static {v6, v7}, Ljava/lang/Math;->abs(D)D

    move-result-wide v6

    invoke-static {v6, v7}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v3

    .line 446
    iget-wide v6, v0, Lio/peakmood/mobile/WorldMapView;->playerLon:D

    cmpl-double v8, v6, v4

    if-ltz v8, :cond_2

    const-string v4, "\u0412"

    goto :goto_1

    :cond_2
    const-string v4, "\u0417"

    :goto_1
    iget-wide v5, v0, Lio/peakmood/mobile/WorldMapView;->playerLon:D

    .line 447
    invoke-static {v5, v6}, Ljava/lang/Math;->abs(D)D

    move-result-wide v5

    invoke-static {v5, v6}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v5

    iget-wide v6, v0, Lio/peakmood/mobile/WorldMapView;->playerAlt:D

    .line 448
    invoke-static {v6, v7}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object v6

    const/4 v7, 0x5

    new-array v7, v7, [Ljava/lang/Object;

    aput-object v2, v7, v13

    aput-object v3, v7, v12

    aput-object v4, v7, v14

    const/4 v2, 0x3

    aput-object v5, v7, v2

    const/4 v2, 0x4

    aput-object v6, v7, v2

    .line 441
    const-string v2, "%s %.4f \u00b7 %s %.4f \u00b7 %.0f \u043c"

    invoke-static {v1, v2, v7}, Ljava/lang/String;->format(Ljava/util/Locale;Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    .line 452
    :goto_2
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    invoke-virtual {v2, v1}, Landroid/graphics/Paint;->measureText(Ljava/lang/String;)F

    move-result v2

    .line 453
    invoke-direct {v0, v10, v11}, Lio/peakmood/mobile/WorldMapView;->isCompactMap(FF)Z

    move-result v3

    if-eqz v3, :cond_3

    const/high16 v3, 0x41200000    # 10.0f

    goto :goto_3

    :cond_3
    const/high16 v3, 0x43140000    # 148.0f

    :goto_3
    invoke-direct {v0, v3}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v3

    sub-float v3, v11, v3

    .line 454
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    const/16 v5, 0x78

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 455
    const/high16 v4, 0x40000000    # 2.0f

    div-float v5, v10, v4

    div-float/2addr v2, v4

    sub-float/2addr v5, v2

    const/high16 v2, 0x3fc00000    # 1.5f

    invoke-direct {v0, v2}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v2

    add-float/2addr v2, v3

    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    invoke-virtual {v9, v1, v5, v2, v4}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 456
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    const/16 v4, 0xe4

    invoke-virtual {v2, v4}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 457
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->captionPaint:Landroid/graphics/Paint;

    invoke-virtual {v9, v1, v5, v3, v2}, Landroid/graphics/Canvas;->drawText(Ljava/lang/String;FFLandroid/graphics/Paint;)V

    .line 458
    return-void
.end method

.method private drawFallbackMap(Landroid/graphics/Canvas;FF)V
    .locals 12

    .line 290
    const/4 v2, 0x0

    iget-object v5, p0, Lio/peakmood/mobile/WorldMapView;->tilePlaceholderPaint:Landroid/graphics/Paint;

    const/4 v1, 0x0

    move-object v0, p1

    move v3, p2

    move v4, p3

    invoke-virtual/range {v0 .. v5}, Landroid/graphics/Canvas;->drawRect(FFFFLandroid/graphics/Paint;)V

    .line 291
    move-object v6, v0

    move v9, v3

    move v10, v4

    const/4 v8, 0x0

    iget-object v11, p0, Lio/peakmood/mobile/WorldMapView;->tileTintPaint:Landroid/graphics/Paint;

    const/4 v7, 0x0

    invoke-virtual/range {v6 .. v11}, Landroid/graphics/Canvas;->drawRect(FFFFLandroid/graphics/Paint;)V

    .line 293
    const/high16 p1, 0x42900000    # 72.0f

    invoke-direct {p0, p1}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result p1

    invoke-static {v3, v10}, Ljava/lang/Math;->min(FF)F

    move-result p2

    const/high16 p3, 0x40800000    # 4.0f

    div-float/2addr p2, p3

    invoke-static {p1, p2}, Ljava/lang/Math;->max(FF)F

    move-result p1

    .line 294
    const/4 p2, 0x0

    const/4 v7, 0x0

    :goto_0
    cmpg-float p3, v7, v3

    if-gtz p3, :cond_0

    .line 295
    const/4 v8, 0x0

    iget-object v11, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    move v9, v7

    invoke-virtual/range {v6 .. v11}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 294
    move v4, v10

    add-float/2addr v7, p1

    goto :goto_0

    .line 297
    :cond_0
    move v4, v10

    const/4 v8, 0x0

    :goto_1
    cmpg-float p2, v8, v4

    if-gtz p2, :cond_1

    .line 298
    const/4 v7, 0x0

    iget-object v11, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    move v10, v8

    move v9, v3

    invoke-virtual/range {v6 .. v11}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 297
    add-float/2addr v8, p1

    goto :goto_1

    .line 300
    :cond_1
    return-void
.end method

.method private drawNode(Landroid/graphics/Canvas;IFFFF)V
    .locals 10

    .line 391
    iget-boolean v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeActive:Z

    if-eqz v1, :cond_8

    iget-wide v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeLat:D

    invoke-static {v1, v2}, Ljava/lang/Double;->isNaN(D)Z

    move-result v1

    if-nez v1, :cond_8

    iget-wide v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeLon:D

    invoke-static {v1, v2}, Ljava/lang/Double;->isNaN(D)Z

    move-result v1

    if-eqz v1, :cond_0

    goto/16 :goto_5

    .line 395
    :cond_0
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getWidth()I

    move-result v1

    int-to-float v1, v1

    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getHeight()I

    move-result v2

    int-to-float v2, v2

    invoke-direct {p0, v1, v2}, Lio/peakmood/mobile/WorldMapView;->isCompactMap(FF)Z

    move-result v6

    .line 396
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v1

    .line 397
    iget-wide v3, p0, Lio/peakmood/mobile/WorldMapView;->nodeLon:D

    invoke-direct {p0, v3, v4, p2}, Lio/peakmood/mobile/WorldMapView;->lonToWorldX(DI)D

    move-result-wide v3

    float-to-double v7, p3

    invoke-static {v7, v8}, Ljava/lang/Double;->isNaN(D)Z

    sub-double/2addr v3, v7

    double-to-float v3, v3

    .line 398
    iget-wide v4, p0, Lio/peakmood/mobile/WorldMapView;->nodeLat:D

    invoke-direct {p0, v4, v5, p2}, Lio/peakmood/mobile/WorldMapView;->latToWorldY(DI)D

    move-result-wide v4

    float-to-double v7, p4

    invoke-static {v7, v8}, Ljava/lang/Double;->isNaN(D)Z

    sub-double/2addr v4, v7

    double-to-float v0, v4

    .line 399
    if-eqz v6, :cond_1

    const/high16 v4, 0x41300000    # 11.0f

    goto :goto_0

    :cond_1
    const/high16 v4, 0x41500000    # 13.0f

    :goto_0
    invoke-direct {p0, v4}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v4

    move v7, v4

    .line 400
    const/high16 v4, 0x41200000    # 10.0f

    invoke-direct {p0, v4}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v5

    add-float/2addr v5, v7

    .line 401
    if-eqz v6, :cond_2

    const/high16 v8, 0x41e00000    # 28.0f

    goto :goto_1

    :cond_2
    const/high16 v8, 0x433c0000    # 188.0f

    :goto_1
    invoke-direct {p0, v8}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v8

    add-float/2addr v8, v7

    .line 402
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getWidth()I

    move-result v9

    int-to-float v9, v9

    sub-float/2addr v9, v5

    invoke-direct {p0, v3, v5, v9}, Lio/peakmood/mobile/WorldMapView;->clamp(FFF)F

    move-result v3

    .line 403
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getHeight()I

    move-result v9

    int-to-float v9, v9

    sub-float/2addr v9, v8

    invoke-direct {p0, v0, v5, v9}, Lio/peakmood/mobile/WorldMapView;->clamp(FFF)F

    move-result v0

    .line 404
    iget-object v5, p0, Lio/peakmood/mobile/WorldMapView;->tier:Ljava/lang/String;

    invoke-direct {p0, v5}, Lio/peakmood/mobile/WorldMapView;->tierColor(Ljava/lang/String;)I

    move-result v8

    .line 405
    long-to-float v1, v1

    const v2, 0x3b89a027    # 0.0042f

    mul-float v1, v1, v2

    float-to-double v1, v1

    invoke-static {v1, v2}, Ljava/lang/Math;->sin(D)D

    move-result-wide v1

    double-to-float v1, v1

    const/high16 v2, 0x3f000000    # 0.5f

    mul-float v1, v1, v2

    add-float/2addr v1, v2

    .line 406
    const/high16 v2, 0x40c00000    # 6.0f

    if-eqz v6, :cond_3

    const/high16 v5, 0x40c00000    # 6.0f

    goto :goto_2

    :cond_3
    const/high16 v5, 0x41100000    # 9.0f

    :goto_2
    invoke-direct {p0, v5}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v5

    add-float/2addr v5, v7

    if-eqz v6, :cond_4

    const/high16 v4, 0x40c00000    # 6.0f

    :cond_4
    invoke-direct {p0, v4}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v2

    mul-float v1, v1, v2

    add-float v9, v5, v1

    .line 408
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v8}, Landroid/graphics/Paint;->setColor(I)V

    .line 409
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    if-eqz v6, :cond_5

    const/16 v2, 0xd2

    goto :goto_3

    :cond_5
    const/16 v2, 0xb0

    :goto_3
    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 410
    iget-object v5, p0, Lio/peakmood/mobile/WorldMapView;->nodeTrailPaint:Landroid/graphics/Paint;

    move v1, p5

    move/from16 v2, p6

    move v4, v0

    move-object v0, p1

    invoke-virtual/range {v0 .. v5}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 412
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodePulsePaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v8}, Landroid/graphics/Paint;->setColor(I)V

    .line 413
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodePulsePaint:Landroid/graphics/Paint;

    if-eqz v6, :cond_6

    const/16 v2, 0x48

    goto :goto_4

    :cond_6
    const/16 v2, 0x3a

    :goto_4
    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 414
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodePulsePaint:Landroid/graphics/Paint;

    invoke-virtual {p1, v3, v4, v9, v1}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 416
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodePaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v8}, Landroid/graphics/Paint;->setColor(I)V

    .line 417
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v8}, Landroid/graphics/Paint;->setColor(I)V

    .line 418
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    const/16 v2, 0xe2

    invoke-virtual {v1, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 419
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodePaint:Landroid/graphics/Paint;

    invoke-virtual {p1, v3, v4, v7, v1}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 420
    const/high16 v1, 0x40a00000    # 5.0f

    invoke-direct {p0, v1}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v1

    add-float/2addr v1, v7

    iget-object v2, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, v3, v4, v1, v2}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 421
    const v1, 0x3ed70a3d    # 0.42f

    mul-float v1, v1, v7

    iget-object v2, p0, Lio/peakmood/mobile/WorldMapView;->nodeCorePaint:Landroid/graphics/Paint;

    invoke-virtual {p1, v3, v4, v1, v2}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 423
    iget v1, p0, Lio/peakmood/mobile/WorldMapView;->hpTotal:I

    if-lez v1, :cond_7

    .line 424
    iget v1, p0, Lio/peakmood/mobile/WorldMapView;->hitsLeft:I

    int-to-float v1, v1

    iget v2, p0, Lio/peakmood/mobile/WorldMapView;->hpTotal:I

    int-to-float v2, v2

    div-float/2addr v1, v2

    const/high16 v2, 0x3f800000    # 1.0f

    sub-float/2addr v2, v1

    .line 425
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    sub-float v5, v3, v7

    .line 426
    const/high16 v6, 0x41000000    # 8.0f

    invoke-direct {p0, v6}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v8

    sub-float/2addr v5, v8

    sub-float v8, v4, v7

    .line 427
    invoke-direct {p0, v6}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v9

    sub-float/2addr v8, v9

    add-float/2addr v3, v7

    .line 428
    invoke-direct {p0, v6}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v9

    add-float/2addr v3, v9

    add-float/2addr v4, v7

    .line 429
    invoke-direct {p0, v6}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v6

    add-float/2addr v4, v6

    .line 425
    invoke-virtual {v1, v5, v8, v3, v4}, Landroid/graphics/RectF;->set(FFFF)V

    .line 431
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    const/16 v3, 0xff

    invoke-virtual {v1, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 432
    iget-object v1, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    const/high16 v3, 0x43b40000    # 360.0f

    mul-float v3, v3, v2

    const/4 v4, 0x0

    iget-object v5, p0, Lio/peakmood/mobile/WorldMapView;->nodeRingPaint:Landroid/graphics/Paint;

    const/high16 v2, -0x3d4c0000    # -90.0f

    move-object v0, p1

    invoke-virtual/range {v0 .. v5}, Landroid/graphics/Canvas;->drawArc(Landroid/graphics/RectF;FFZLandroid/graphics/Paint;)V

    .line 434
    :cond_7
    return-void

    .line 392
    :cond_8
    :goto_5
    return-void
.end method

.method private drawPlaceholderTile(Landroid/graphics/Canvas;Landroid/graphics/RectF;)V
    .locals 13

    .line 284
    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView;->tilePlaceholderPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, v0}, Landroid/graphics/Canvas;->drawRect(Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    .line 285
    iget v2, p2, Landroid/graphics/RectF;->left:F

    iget v3, p2, Landroid/graphics/RectF;->top:F

    iget v4, p2, Landroid/graphics/RectF;->right:F

    iget v5, p2, Landroid/graphics/RectF;->bottom:F

    iget-object v6, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    move-object v1, p1

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 286
    iget v8, p2, Landroid/graphics/RectF;->left:F

    iget v9, p2, Landroid/graphics/RectF;->bottom:F

    iget v10, p2, Landroid/graphics/RectF;->right:F

    iget v11, p2, Landroid/graphics/RectF;->top:F

    iget-object v12, p0, Lio/peakmood/mobile/WorldMapView;->tileGridPaint:Landroid/graphics/Paint;

    move-object v7, v1

    invoke-virtual/range {v7 .. v12}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 287
    return-void
.end method

.method private drawPlayer(Landroid/graphics/Canvas;FFZ)V
    .locals 9

    .line 366
    iget-boolean v0, p0, Lio/peakmood/mobile/WorldMapView;->hasLocation:Z

    if-nez v0, :cond_0

    .line 367
    return-void

    .line 370
    :cond_0
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 371
    if-eqz p4, :cond_1

    const/high16 v2, 0x41200000    # 10.0f

    goto :goto_0

    :cond_1
    const/high16 v2, 0x41300000    # 11.0f

    :goto_0
    invoke-direct {p0, v2}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v2

    .line 372
    const/4 v3, 0x0

    :goto_1
    const/4 v4, 0x3

    if-ge v3, v4, :cond_4

    .line 373
    const-wide/16 v4, 0x960

    rem-long v4, v0, v4

    long-to-float v4, v4

    const/high16 v5, 0x45160000    # 2400.0f

    div-float/2addr v4, v5

    int-to-float v5, v3

    const/high16 v6, 0x40400000    # 3.0f

    div-float/2addr v5, v6

    add-float/2addr v4, v5

    const/high16 v5, 0x3f800000    # 1.0f

    rem-float/2addr v4, v5

    .line 374
    mul-float v7, v4, v4

    const/high16 v8, 0x40000000    # 2.0f

    mul-float v8, v8, v4

    sub-float/2addr v6, v8

    mul-float v7, v7, v6

    .line 375
    if-eqz p4, :cond_2

    .line 376
    const/high16 v6, 0x41600000    # 14.0f

    invoke-direct {p0, v6}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v6

    const/high16 v8, 0x42680000    # 58.0f

    invoke-direct {p0, v8}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v8

    invoke-direct {p0, v6, v8, v7}, Lio/peakmood/mobile/WorldMapView;->lerp(FFF)F

    move-result v6

    goto :goto_2

    .line 377
    :cond_2
    const/high16 v6, 0x41900000    # 18.0f

    invoke-direct {p0, v6}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v6

    const/high16 v8, 0x43000000    # 128.0f

    invoke-direct {p0, v8}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v8

    invoke-direct {p0, v6, v8, v7}, Lio/peakmood/mobile/WorldMapView;->lerp(FFF)F

    move-result v6

    .line 378
    :goto_2
    sub-float/2addr v5, v4

    .line 379
    mul-float v5, v5, v5

    .line 380
    iget-object v4, p0, Lio/peakmood/mobile/WorldMapView;->ripplePaint:Landroid/graphics/Paint;

    if-eqz p4, :cond_3

    const/16 v7, 0x6c

    goto :goto_3

    :cond_3
    const/16 v7, 0x60

    :goto_3
    int-to-float v7, v7

    mul-float v7, v7, v5

    float-to-int v5, v7

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 381
    iget-object v4, p0, Lio/peakmood/mobile/WorldMapView;->ripplePaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, p3, v6, v4}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 372
    add-int/lit8 v3, v3, 0x1

    goto :goto_1

    .line 383
    :cond_4
    if-eqz p4, :cond_5

    .line 384
    iget-object p4, p0, Lio/peakmood/mobile/WorldMapView;->playerHaloPaint:Landroid/graphics/Paint;

    const/16 v0, 0xc0

    invoke-virtual {p4, v0}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 385
    const/high16 p4, 0x41a00000    # 20.0f

    invoke-direct {p0, p4}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result p4

    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView;->playerHaloPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, p3, p4, v0}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 387
    :cond_5
    iget-object p4, p0, Lio/peakmood/mobile/WorldMapView;->playerPaint:Landroid/graphics/Paint;

    invoke-virtual {p1, p2, p3, v2, p4}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 388
    return-void
.end method

.method private drawRadarScope(Landroid/graphics/Canvas;FFFFZ)V
    .locals 17

    .line 303
    move-object/from16 v0, p0

    move-object/from16 v1, p1

    move/from16 v7, p4

    move/from16 v8, p5

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v9

    .line 304
    const/high16 v11, 0x43b40000    # 360.0f

    const/16 v2, 0x60

    if-eqz p6, :cond_1

    .line 305
    invoke-static/range {p2 .. p3}, Ljava/lang/Math;->min(FF)F

    move-result v3

    const v4, 0x3ee147ae    # 0.44f

    mul-float v3, v3, v4

    .line 306
    const/high16 v4, 0x40400000    # 3.0f

    div-float v12, v3, v4

    .line 308
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    const/16 v5, 0x22

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 309
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7, v8, v3, v4}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 311
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const/high16 v5, 0x3fc00000    # 1.5f

    invoke-direct {v0, v5}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v5

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 312
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v4, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 313
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7, v8, v3, v2}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 315
    invoke-virtual {v1}, Landroid/graphics/Canvas;->save()I

    move-result v13

    .line 316
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    invoke-virtual {v2}, Landroid/graphics/Path;->reset()V

    .line 317
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    sget-object v4, Landroid/graphics/Path$Direction;->CW:Landroid/graphics/Path$Direction;

    invoke-virtual {v2, v7, v8, v3, v4}, Landroid/graphics/Path;->addCircle(FFFLandroid/graphics/Path$Direction;)V

    .line 318
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    invoke-virtual {v1, v2}, Landroid/graphics/Canvas;->clipPath(Landroid/graphics/Path;)Z

    .line 320
    const-wide/16 v4, 0xc80

    rem-long/2addr v9, v4

    long-to-float v2, v9

    const/high16 v4, 0x45480000    # 3200.0f

    div-float/2addr v2, v4

    mul-float v9, v2, v11

    .line 321
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    sub-float v10, v7, v3

    sub-float v11, v8, v3

    add-float v14, v7, v3

    add-float v15, v8, v3

    invoke-virtual {v2, v10, v11, v14, v15}, Landroid/graphics/RectF;->set(FFFF)V

    .line 322
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    const/16 v3, 0x56

    invoke-virtual {v2, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 323
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const/16 v3, 0xd2

    invoke-virtual {v2, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 324
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    const/high16 v3, 0x41a00000    # 20.0f

    sub-float v3, v9, v3

    const/4 v5, 0x1

    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    const/high16 v4, 0x41a00000    # 20.0f

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawArc(Landroid/graphics/RectF;FFZLandroid/graphics/Paint;)V

    .line 325
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    const v1, 0x3fe66666    # 1.8f

    sub-float v3, v9, v1

    const/4 v5, 0x0

    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const v4, 0x3fe66666    # 1.8f

    move-object/from16 v1, p1

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawArc(Landroid/graphics/RectF;FFZLandroid/graphics/Paint;)V

    .line 326
    invoke-virtual {v1, v13}, Landroid/graphics/Canvas;->restoreToCount(I)V

    .line 328
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const/16 v3, 0x4e

    invoke-virtual {v2, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 329
    const/4 v2, 0x1

    :goto_0
    const/4 v3, 0x3

    if-gt v2, v3, :cond_0

    .line 330
    int-to-float v3, v2

    mul-float v3, v3, v12

    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7, v8, v3, v4}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 329
    add-int/lit8 v2, v2, 0x1

    goto :goto_0

    .line 332
    :cond_0
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    const/16 v3, 0x7e

    invoke-virtual {v2, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 333
    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    move/from16 v5, p5

    move v3, v8

    move v2, v10

    move v4, v14

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 334
    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    move/from16 v4, p4

    move-object/from16 v1, p1

    move v2, v7

    move v3, v11

    move v5, v15

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 335
    return-void

    .line 338
    :cond_1
    move v3, v8

    move/from16 v4, p2

    float-to-double v4, v4

    move/from16 v6, p3

    float-to-double v12, v6

    invoke-static {v4, v5, v12, v13}, Ljava/lang/Math;->hypot(DD)D

    move-result-wide v4

    double-to-float v4, v4

    const v5, 0x3f147ae1    # 0.58f

    mul-float v8, v4, v5

    .line 339
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    const/16 v5, 0x12

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 340
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->scopeFillPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7, v3, v8, v4}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 342
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const/16 v5, 0x48

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 343
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const v5, 0x3fcccccd    # 1.6f

    invoke-direct {v0, v5}, Lio/peakmood/mobile/WorldMapView;->dp(F)F

    move-result v5

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setStrokeWidth(F)V

    .line 344
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7, v3, v8, v4}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 345
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    const/16 v5, 0x36

    invoke-virtual {v4, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 346
    const v4, 0x3f3851ec    # 0.72f

    mul-float v4, v4, v8

    iget-object v5, v0, Lio/peakmood/mobile/WorldMapView;->ringPaint:Landroid/graphics/Paint;

    invoke-virtual {v1, v7, v3, v4, v5}, Landroid/graphics/Canvas;->drawCircle(FFFLandroid/graphics/Paint;)V

    .line 347
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    invoke-virtual {v4, v2}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 348
    sub-float v2, v7, v8

    add-float v4, v7, v8

    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    move/from16 v5, p5

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 349
    move v13, v2

    move v12, v3

    move v14, v4

    sub-float v3, v12, v8

    add-float v5, v12, v8

    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->tickPaint:Landroid/graphics/Paint;

    move/from16 v4, p4

    move-object/from16 v1, p1

    move v2, v7

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawLine(FFFFLandroid/graphics/Paint;)V

    .line 351
    invoke-virtual {v1}, Landroid/graphics/Canvas;->save()I

    move-result v7

    .line 352
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    invoke-virtual {v4}, Landroid/graphics/Path;->reset()V

    .line 353
    iget-object v4, v0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    sget-object v6, Landroid/graphics/Path$Direction;->CW:Landroid/graphics/Path$Direction;

    invoke-virtual {v4, v2, v12, v8, v6}, Landroid/graphics/Path;->addCircle(FFFLandroid/graphics/Path$Direction;)V

    .line 354
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->scopeClipPath:Landroid/graphics/Path;

    invoke-virtual {v1, v2}, Landroid/graphics/Canvas;->clipPath(Landroid/graphics/Path;)Z

    .line 356
    const-wide/16 v15, 0x1068

    rem-long/2addr v9, v15

    long-to-float v2, v9

    const v4, 0x45834000    # 4200.0f

    div-float/2addr v2, v4

    mul-float v8, v2, v11

    .line 357
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    invoke-virtual {v2, v13, v3, v14, v5}, Landroid/graphics/RectF;->set(FFFF)V

    .line 358
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    const/16 v3, 0x26

    invoke-virtual {v2, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 359
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const/16 v3, 0xb8

    invoke-virtual {v2, v3}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 360
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    const/high16 v3, 0x41600000    # 14.0f

    sub-float v3, v8, v3

    const/4 v5, 0x1

    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->sweepFillPaint:Landroid/graphics/Paint;

    const/high16 v4, 0x41600000    # 14.0f

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawArc(Landroid/graphics/RectF;FFZLandroid/graphics/Paint;)V

    .line 361
    iget-object v2, v0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    const v1, 0x3f666666    # 0.9f

    sub-float v3, v8, v1

    const/4 v5, 0x0

    iget-object v6, v0, Lio/peakmood/mobile/WorldMapView;->sweepEdgePaint:Landroid/graphics/Paint;

    const v4, 0x3f666666    # 0.9f

    move-object/from16 v1, p1

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawArc(Landroid/graphics/RectF;FFZLandroid/graphics/Paint;)V

    .line 362
    invoke-virtual {v1, v7}, Landroid/graphics/Canvas;->restoreToCount(I)V

    .line 363
    return-void
.end method

.method private drawVisibleTiles(Landroid/graphics/Canvas;IFFFF)V
    .locals 12

    .line 255
    const/4 v0, 0x1

    shl-int/2addr v0, p2

    .line 256
    const/high16 v1, 0x43800000    # 256.0f

    div-float v2, p3, v1

    float-to-double v2, v2

    invoke-static {v2, v3}, Ljava/lang/Math;->floor(D)D

    move-result-wide v2

    double-to-int v2, v2

    .line 257
    div-float v3, p4, v1

    float-to-double v3, v3

    invoke-static {v3, v4}, Ljava/lang/Math;->floor(D)D

    move-result-wide v3

    double-to-int v3, v3

    .line 258
    add-float v4, p3, p5

    div-float/2addr v4, v1

    float-to-double v4, v4

    invoke-static {v4, v5}, Ljava/lang/Math;->floor(D)D

    move-result-wide v4

    double-to-int v4, v4

    .line 259
    add-float v5, p4, p6

    div-float/2addr v5, v1

    float-to-double v5, v5

    invoke-static {v5, v6}, Ljava/lang/Math;->floor(D)D

    move-result-wide v5

    double-to-int v5, v5

    .line 261
    nop

    :goto_0
    if-gt v3, v5, :cond_4

    .line 262
    move v6, v2

    :goto_1
    if-gt v6, v4, :cond_3

    .line 263
    mul-int/lit16 v7, v6, 0x100

    int-to-float v7, v7

    sub-float/2addr v7, p3

    .line 264
    mul-int/lit16 v8, v3, 0x100

    int-to-float v8, v8

    sub-float v8, v8, p4

    .line 265
    iget-object v9, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    add-float v10, v7, v1

    add-float v11, v8, v1

    invoke-virtual {v9, v7, v8, v10, v11}, Landroid/graphics/RectF;->set(FFFF)V

    .line 267
    if-ltz v3, :cond_2

    if-lt v3, v0, :cond_0

    goto :goto_2

    .line 272
    :cond_0
    invoke-direct {p0, v6, v0}, Lio/peakmood/mobile/WorldMapView;->wrapTileX(II)I

    move-result v7

    .line 273
    invoke-direct {p0, p2, v7, v3}, Lio/peakmood/mobile/WorldMapView;->loadTileBitmap(III)Landroid/graphics/Bitmap;

    move-result-object v7

    .line 274
    if-nez v7, :cond_1

    .line 275
    iget-object v7, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    invoke-direct {p0, p1, v7}, Lio/peakmood/mobile/WorldMapView;->drawPlaceholderTile(Landroid/graphics/Canvas;Landroid/graphics/RectF;)V

    goto :goto_3

    .line 277
    :cond_1
    iget-object v8, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    const/4 v9, 0x0

    invoke-virtual {p1, v7, v9, v8, v9}, Landroid/graphics/Canvas;->drawBitmap(Landroid/graphics/Bitmap;Landroid/graphics/Rect;Landroid/graphics/RectF;Landroid/graphics/Paint;)V

    goto :goto_3

    .line 268
    :cond_2
    :goto_2
    iget-object v7, p0, Lio/peakmood/mobile/WorldMapView;->workingRect:Landroid/graphics/RectF;

    invoke-direct {p0, p1, v7}, Lio/peakmood/mobile/WorldMapView;->drawPlaceholderTile(Landroid/graphics/Canvas;Landroid/graphics/RectF;)V

    .line 269
    nop

    .line 262
    :goto_3
    add-int/lit8 v6, v6, 0x1

    goto :goto_1

    .line 261
    :cond_3
    add-int/lit8 v3, v3, 0x1

    goto :goto_0

    .line 281
    :cond_4
    return-void
.end method

.method private getColor(I)I
    .locals 1

    .line 653
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getResources()Landroid/content/res/Resources;

    move-result-object v0

    invoke-virtual {v0, p1}, Landroid/content/res/Resources;->getColor(I)I

    move-result p1

    return p1
.end method

.method private isCompactMap(FF)Z
    .locals 3

    .line 571
    iget v0, p0, Lio/peakmood/mobile/WorldMapView;->viewportMode:I

    const/4 v1, 0x2

    const/4 v2, 0x1

    if-ne v0, v1, :cond_0

    .line 572
    return v2

    .line 574
    :cond_0
    iget v0, p0, Lio/peakmood/mobile/WorldMapView;->viewportMode:I

    const/4 v1, 0x0

    if-ne v0, v2, :cond_1

    .line 575
    return v1

    .line 577
    :cond_1
    invoke-static {p1, p2}, Ljava/lang/Math;->min(FF)F

    move-result p1

    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getResources()Landroid/content/res/Resources;

    move-result-object p2

    invoke-virtual {p2}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object p2

    iget p2, p2, Landroid/util/DisplayMetrics;->density:F

    div-float/2addr p1, p2

    const/high16 p2, 0x435c0000    # 220.0f

    cmpg-float p1, p1, p2

    if-gez p1, :cond_2

    goto :goto_0

    :cond_2
    const/4 v2, 0x0

    :goto_0
    return v2
.end method

.method private latToWorldY(DI)D
    .locals 6

    .line 586
    const-wide v0, 0x40554345b1a57f00L    # 85.05112878

    invoke-static {v0, v1, p1, p2}, Ljava/lang/Math;->min(DD)D

    move-result-wide p1

    const-wide v0, -0x3faabcba4e5a8100L    # -85.05112878

    invoke-static {v0, v1, p1, p2}, Ljava/lang/Math;->max(DD)D

    move-result-wide p1

    .line 587
    invoke-static {p1, p2}, Ljava/lang/Math;->toRadians(D)D

    move-result-wide p1

    .line 588
    const-wide/high16 v0, 0x4000000000000000L    # 2.0

    div-double/2addr p1, v0

    const-wide v2, 0x3fe921fb54442d18L    # 0.7853981633974483

    add-double/2addr p1, v2

    invoke-static {p1, p2}, Ljava/lang/Math;->tan(D)D

    move-result-wide p1

    invoke-static {p1, p2}, Ljava/lang/Math;->log(D)D

    move-result-wide p1

    .line 589
    const/4 v2, 0x1

    shl-int p3, v2, p3

    int-to-double v2, p3

    .line 590
    const-wide v4, 0x400921fb54442d18L    # Math.PI

    div-double/2addr p1, v4

    const-wide/high16 v4, 0x3ff0000000000000L    # 1.0

    sub-double/2addr v4, p1

    div-double/2addr v4, v0

    invoke-static {v2, v3}, Ljava/lang/Double;->isNaN(D)Z

    mul-double v4, v4, v2

    const-wide/high16 p1, 0x4070000000000000L    # 256.0

    mul-double v4, v4, p1

    return-wide v4
.end method

.method private lerp(FFF)F
    .locals 0

    .line 602
    sub-float/2addr p2, p1

    mul-float p2, p2, p3

    add-float/2addr p1, p2

    return p1
.end method

.method private loadTileBitmap(III)Landroid/graphics/Bitmap;
    .locals 7

    .line 467
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "_"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    .line 468
    sget-object v0, Lio/peakmood/mobile/WorldMapView;->MEMORY_CACHE:Ljava/util/Map;

    invoke-interface {v0, v2}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/graphics/Bitmap;

    .line 469
    if-eqz v0, :cond_0

    invoke-virtual {v0}, Landroid/graphics/Bitmap;->isRecycled()Z

    move-result v1

    if-nez v1, :cond_0

    .line 470
    return-object v0

    .line 473
    :cond_0
    new-instance v6, Ljava/io/File;

    iget-object v0, p0, Lio/peakmood/mobile/WorldMapView;->diskCacheDir:Ljava/io/File;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v3, ".png"

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v6, v0, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 474
    invoke-virtual {v6}, Ljava/io/File;->isFile()Z

    move-result v0

    if-eqz v0, :cond_2

    .line 475
    invoke-virtual {v6}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Landroid/graphics/BitmapFactory;->decodeFile(Ljava/lang/String;)Landroid/graphics/Bitmap;

    move-result-object v0

    .line 476
    if-eqz v0, :cond_1

    .line 477
    sget-object p1, Lio/peakmood/mobile/WorldMapView;->MEMORY_CACHE:Ljava/util/Map;

    invoke-interface {p1, v2, v0}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 478
    return-object v0

    .line 481
    :cond_1
    invoke-virtual {v6}, Ljava/io/File;->delete()Z

    .line 484
    :cond_2
    move-object v1, p0

    move v3, p1

    move v4, p2

    move v5, p3

    invoke-direct/range {v1 .. v6}, Lio/peakmood/mobile/WorldMapView;->queueTileFetch(Ljava/lang/String;IIILjava/io/File;)V

    .line 485
    const/4 p1, 0x0

    return-object p1
.end method

.method private lonToWorldX(DI)D
    .locals 4

    .line 581
    const/4 v0, 0x1

    shl-int p3, v0, p3

    int-to-double v0, p3

    .line 582
    const-wide v2, 0x4066800000000000L    # 180.0

    add-double/2addr p1, v2

    const-wide v2, 0x4076800000000000L    # 360.0

    div-double/2addr p1, v2

    invoke-static {v0, v1}, Ljava/lang/Double;->isNaN(D)Z

    mul-double p1, p1, v0

    const-wide/high16 v0, 0x4070000000000000L    # 256.0

    mul-double p1, p1, v0

    return-wide p1
.end method

.method private queueTileFetch(Ljava/lang/String;IIILjava/io/File;)V
    .locals 8

    .line 489
    sget-object v0, Lio/peakmood/mobile/WorldMapView;->IN_FLIGHT:Ljava/util/Set;

    invoke-interface {v0, p1}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    .line 490
    return-void

    .line 493
    :cond_0
    sget-object v0, Lio/peakmood/mobile/WorldMapView;->TILE_EXECUTOR:Ljava/util/concurrent/ExecutorService;

    new-instance v1, Lio/peakmood/mobile/WorldMapView$2;

    move-object v2, p0

    move-object v7, p1

    move v3, p2

    move v4, p3

    move v5, p4

    move-object v6, p5

    invoke-direct/range {v1 .. v7}, Lio/peakmood/mobile/WorldMapView$2;-><init>(Lio/peakmood/mobile/WorldMapView;IIILjava/io/File;Ljava/lang/String;)V

    invoke-interface {v0, v1}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    .line 510
    return-void
.end method

.method private resolveZoomLevel(FF)I
    .locals 2

    .line 557
    iget v0, p0, Lio/peakmood/mobile/WorldMapView;->zoomLevelOverride:I

    const/16 v1, 0x11

    if-lez v0, :cond_0

    .line 558
    iget p1, p0, Lio/peakmood/mobile/WorldMapView;->zoomLevelOverride:I

    invoke-static {p1, v1}, Ljava/lang/Math;->min(II)I

    move-result p1

    return p1

    .line 560
    :cond_0
    invoke-static {p1, p2}, Ljava/lang/Math;->min(FF)F

    move-result p1

    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getResources()Landroid/content/res/Resources;

    move-result-object p2

    invoke-virtual {p2}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object p2

    iget p2, p2, Landroid/util/DisplayMetrics;->density:F

    div-float/2addr p1, p2

    .line 561
    const/high16 p2, 0x43340000    # 180.0f

    cmpg-float p2, p1, p2

    if-gez p2, :cond_1

    .line 562
    return v1

    .line 564
    :cond_1
    const/high16 p2, 0x43a00000    # 320.0f

    cmpg-float p1, p1, p2

    if-gez p1, :cond_2

    .line 565
    return v1

    .line 567
    :cond_2
    return v1
.end method

.method private tierColor(Ljava/lang/String;)I
    .locals 1

    .line 637
    const-string v0, "common"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 638
    const p1, 0x7f050010

    invoke-direct {p0, p1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result p1

    return p1

    .line 640
    :cond_0
    const-string v0, "rare"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 641
    const p1, 0x7f050011

    invoke-direct {p0, p1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result p1

    return p1

    .line 643
    :cond_1
    const-string v0, "epic"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    .line 644
    const p1, 0x7f050012

    invoke-direct {p0, p1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result p1

    return p1

    .line 646
    :cond_2
    const-string v0, "FLAG"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    .line 647
    const p1, 0x7f050013

    invoke-direct {p0, p1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result p1

    return p1

    .line 649
    :cond_3
    const p1, 0x7f05000d

    invoke-direct {p0, p1}, Lio/peakmood/mobile/WorldMapView;->getColor(I)I

    move-result p1

    return p1
.end method

.method private tierLabel(Ljava/lang/String;)Ljava/lang/String;
    .locals 1

    .line 610
    const-string v0, "common"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    .line 611
    const-string p1, "\u041e\u0431\u044b\u0447\u043d\u0430\u044f \u043d\u0430\u0445\u043e\u0434\u043a\u0430"

    return-object p1

    .line 613
    :cond_0
    const-string v0, "rare"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 614
    const-string p1, "\u0420\u0435\u0434\u043a\u0430\u044f \u043d\u0430\u0445\u043e\u0434\u043a\u0430"

    return-object p1

    .line 616
    :cond_1
    const-string v0, "epic"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2

    .line 617
    const-string p1, "\u042d\u043f\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043d\u0430\u0445\u043e\u0434\u043a\u0430"

    return-object p1

    .line 619
    :cond_2
    const-string v0, "FLAG"

    invoke-virtual {v0, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_3

    .line 620
    const-string p1, "\u041c\u0438\u0444\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043d\u0430\u0445\u043e\u0434\u043a\u0430"

    return-object p1

    .line 622
    :cond_3
    const-string p1, "\u0421\u043a\u0430\u043d\u0438\u0440\u0443\u0435\u043c \u043c\u0435\u0441\u0442\u043d\u043e\u0441\u0442\u044c..."

    return-object p1
.end method

.method private wrapTileX(II)I
    .locals 0

    .line 594
    rem-int/2addr p1, p2

    .line 595
    if-gez p1, :cond_0

    .line 596
    add-int/2addr p1, p2

    .line 598
    :cond_0
    return p1
.end method


# virtual methods
.method protected onDraw(Landroid/graphics/Canvas;)V
    .locals 13

    .line 219
    invoke-super {p0, p1}, Landroid/view/View;->onDraw(Landroid/graphics/Canvas;)V

    .line 221
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getWidth()I

    move-result v0

    int-to-float v3, v0

    .line 222
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->getHeight()I

    move-result v0

    int-to-float v4, v0

    .line 223
    const/4 v0, 0x0

    cmpg-float v1, v3, v0

    if-lez v1, :cond_3

    cmpg-float v0, v4, v0

    if-gtz v0, :cond_0

    move-object v1, p0

    goto/16 :goto_1

    .line 227
    :cond_0
    iget-boolean v0, p0, Lio/peakmood/mobile/WorldMapView;->hasLocation:Z

    if-nez v0, :cond_1

    .line 228
    invoke-direct {p0, p1, v3, v4}, Lio/peakmood/mobile/WorldMapView;->drawFallbackMap(Landroid/graphics/Canvas;FF)V

    .line 229
    invoke-direct {p0, p1, v3, v4}, Lio/peakmood/mobile/WorldMapView;->drawAttribution(Landroid/graphics/Canvas;FF)V

    .line 230
    return-void

    .line 233
    :cond_1
    invoke-direct {p0, v3, v4}, Lio/peakmood/mobile/WorldMapView;->isCompactMap(FF)Z

    move-result v0

    .line 234
    invoke-direct {p0, v3, v4}, Lio/peakmood/mobile/WorldMapView;->resolveZoomLevel(FF)I

    move-result v7

    .line 235
    iget-wide v1, p0, Lio/peakmood/mobile/WorldMapView;->playerLon:D

    invoke-direct {p0, v1, v2, v7}, Lio/peakmood/mobile/WorldMapView;->lonToWorldX(DI)D

    move-result-wide v1

    .line 236
    iget-wide v5, p0, Lio/peakmood/mobile/WorldMapView;->playerLat:D

    invoke-direct {p0, v5, v6, v7}, Lio/peakmood/mobile/WorldMapView;->latToWorldY(DI)D

    move-result-wide v5

    .line 237
    const/high16 v8, 0x40000000    # 2.0f

    div-float v10, v3, v8

    .line 238
    div-float v11, v4, v8

    .line 239
    float-to-double v8, v10

    invoke-static {v8, v9}, Ljava/lang/Double;->isNaN(D)Z

    sub-double/2addr v1, v8

    double-to-float v8, v1

    .line 240
    float-to-double v1, v11

    invoke-static {v1, v2}, Ljava/lang/Double;->isNaN(D)Z

    sub-double/2addr v5, v1

    double-to-float v5, v5

    .line 242
    move-object v1, p0

    move-object v2, p1

    move v6, v3

    move v3, v7

    move v7, v4

    move v4, v8

    invoke-direct/range {v1 .. v7}, Lio/peakmood/mobile/WorldMapView;->drawVisibleTiles(Landroid/graphics/Canvas;IFFFF)V

    .line 243
    move-object p1, v1

    move v8, v3

    move v9, v4

    move v12, v5

    move v3, v6

    move v4, v7

    iget-object v1, p1, Lio/peakmood/mobile/WorldMapView;->tileTintPaint:Landroid/graphics/Paint;

    if-eqz v0, :cond_2

    const/16 v5, 0x3e

    goto :goto_0

    :cond_2
    const/16 v5, 0xc

    :goto_0
    invoke-virtual {v1, v5}, Landroid/graphics/Paint;->setAlpha(I)V

    .line 244
    move v6, v3

    const/4 v3, 0x0

    move v5, v4

    move v4, v6

    iget-object v6, p1, Lio/peakmood/mobile/WorldMapView;->tileTintPaint:Landroid/graphics/Paint;

    move-object v1, v2

    const/4 v2, 0x0

    invoke-virtual/range {v1 .. v6}, Landroid/graphics/Canvas;->drawRect(FFFFLandroid/graphics/Paint;)V

    .line 245
    move-object v2, v1

    move v3, v4

    move v4, v5

    move-object v1, p1

    move v7, v0

    move v5, v10

    move v6, v11

    invoke-direct/range {v1 .. v7}, Lio/peakmood/mobile/WorldMapView;->drawRadarScope(Landroid/graphics/Canvas;FFFFZ)V

    .line 246
    move p1, v7

    move v7, v8

    move v8, v9

    move v9, v12

    move-object v5, p0

    move-object v6, v2

    invoke-direct/range {v5 .. v11}, Lio/peakmood/mobile/WorldMapView;->drawNode(Landroid/graphics/Canvas;IFFFF)V

    .line 247
    move-object v1, v5

    move v5, v10

    move v6, v11

    invoke-direct {p0, v2, v5, v6, p1}, Lio/peakmood/mobile/WorldMapView;->drawPlayer(Landroid/graphics/Canvas;FFZ)V

    .line 248
    invoke-direct {p0, v2, v3, v4}, Lio/peakmood/mobile/WorldMapView;->drawCaption(Landroid/graphics/Canvas;FF)V

    .line 249
    invoke-direct {p0, v2, v3, v4}, Lio/peakmood/mobile/WorldMapView;->drawAttribution(Landroid/graphics/Canvas;FF)V

    .line 251
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->postInvalidateOnAnimation()V

    .line 252
    return-void

    .line 223
    :cond_3
    move-object v1, p0

    .line 224
    :goto_1
    return-void
.end method

.method public setNodeState(ZLjava/lang/String;Ljava/lang/String;IIDD)V
    .locals 0

    .line 207
    iput-boolean p1, p0, Lio/peakmood/mobile/WorldMapView;->nodeActive:Z

    .line 208
    if-nez p2, :cond_0

    const-string p2, ""

    :cond_0
    iput-object p2, p0, Lio/peakmood/mobile/WorldMapView;->nodeId:Ljava/lang/String;

    .line 209
    if-nez p3, :cond_1

    const-string p3, "none"

    :cond_1
    iput-object p3, p0, Lio/peakmood/mobile/WorldMapView;->tier:Ljava/lang/String;

    .line 210
    iput p4, p0, Lio/peakmood/mobile/WorldMapView;->hitsLeft:I

    .line 211
    iput p5, p0, Lio/peakmood/mobile/WorldMapView;->hpTotal:I

    .line 212
    iput-wide p6, p0, Lio/peakmood/mobile/WorldMapView;->nodeLat:D

    .line 213
    iput-wide p8, p0, Lio/peakmood/mobile/WorldMapView;->nodeLon:D

    .line 214
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->invalidate()V

    .line 215
    return-void
.end method

.method public setPlayerLocation(DDD)V
    .locals 1

    .line 191
    const/4 v0, 0x1

    iput-boolean v0, p0, Lio/peakmood/mobile/WorldMapView;->hasLocation:Z

    .line 192
    iput-wide p1, p0, Lio/peakmood/mobile/WorldMapView;->playerLat:D

    .line 193
    iput-wide p3, p0, Lio/peakmood/mobile/WorldMapView;->playerLon:D

    .line 194
    iput-wide p5, p0, Lio/peakmood/mobile/WorldMapView;->playerAlt:D

    .line 195
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->invalidate()V

    .line 196
    return-void
.end method

.method public setViewportMode(I)V
    .locals 0

    .line 181
    iput p1, p0, Lio/peakmood/mobile/WorldMapView;->viewportMode:I

    .line 182
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->invalidate()V

    .line 183
    return-void
.end method

.method public setZoomLevelOverride(I)V
    .locals 1

    .line 186
    if-lez p1, :cond_0

    const/16 v0, 0x11

    invoke-static {p1, v0}, Ljava/lang/Math;->min(II)I

    move-result p1

    :cond_0
    iput p1, p0, Lio/peakmood/mobile/WorldMapView;->zoomLevelOverride:I

    .line 187
    invoke-virtual {p0}, Lio/peakmood/mobile/WorldMapView;->invalidate()V

    .line 188
    return-void
.end method
