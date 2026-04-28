package io.peakmood.mobile;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.Rect;
import android.graphics.RectF;
import android.util.AttributeSet;
import android.util.Log;
import android.view.View;
import java.io.File;
import java.io.IOException;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/* JADX INFO: loaded from: classes.dex */
public class WorldMapView extends View {
    private static final int MAX_TILE_ZOOM = 17;
    private static final String TAG = "WorldMapView";
    private static final int TILE_SIZE = 256;
    private static final String TILE_TEMPLATE = "%s://%s/%d/%d/%d.png";
    public static final int VIEWPORT_AUTO = 0;
    public static final int VIEWPORT_EXPANDED = 1;
    public static final int VIEWPORT_PANEL = 2;
    private final Paint attributionPaint;
    private final Paint captionPaint;
    private final File diskCacheDir;
    private boolean hasLocation;
    private int hitsLeft;
    private int hpTotal;
    private boolean nodeActive;
    private final Paint nodeCorePaint;
    private String nodeId;
    private double nodeLat;
    private double nodeLon;
    private final Paint nodePaint;
    private final Paint nodePulsePaint;
    private final Paint nodeRingPaint;
    private final Paint nodeTrailPaint;
    private double playerAlt;
    private final Paint playerHaloPaint;
    private double playerLat;
    private double playerLon;
    private final Paint playerPaint;
    private final Paint ringPaint;
    private final Paint ripplePaint;
    private final Path scopeClipPath;
    private final Paint scopeFillPaint;
    private final Paint sweepEdgePaint;
    private final Paint sweepFillPaint;
    private final Paint tickPaint;
    private String tier;
    private final Paint tileGridPaint;
    private final Paint tilePlaceholderPaint;
    private final Paint tileTintPaint;
    private int viewportMode;
    private final RectF workingRect;
    private int zoomLevelOverride;
    private static final ExecutorService TILE_EXECUTOR = Executors.newFixedThreadPool(4);
    private static final int MAX_MEMORY_TILES = 128;
    private static final Map<String, Bitmap> MEMORY_CACHE = Collections.synchronizedMap(new LinkedHashMap<String, Bitmap>(MAX_MEMORY_TILES, 0.75f, true) { // from class: io.peakmood.mobile.WorldMapView.1
        @Override // java.util.LinkedHashMap
        protected boolean removeEldestEntry(Map.Entry<String, Bitmap> entry) {
            return size() > WorldMapView.MAX_MEMORY_TILES;
        }
    });
    private static final Set<String> IN_FLIGHT = Collections.newSetFromMap(new ConcurrentHashMap());
    private static final String[] TILE_HOSTS = {"a-tile-opentopomap.alfactf.ru", "b-tile-opentopomap.alfactf.ru", "c-tile-opentopomap.alfactf.ru", "a2-tile-opentopomap.alfactf.ru", "b2-tile-opentopomap.alfactf.ru", "c2-tile-opentopomap.alfactf.ru", "a3-tile-opentopomap.alfactf.ru", "b3-tile-opentopomap.alfactf.ru", "c3-tile-opentopomap.alfactf.ru", "a4-tile-opentopomap.alfactf.ru", "b4-tile-opentopomap.alfactf.ru", "c4-tile-opentopomap.alfactf.ru"};
    private static final String[] TILE_SCHEMES = {"https", "http"};

    public WorldMapView(Context context) {
        this(context, null);
    }

    public WorldMapView(Context context, AttributeSet attributeSet) {
        super(context, attributeSet);
        this.tilePlaceholderPaint = new Paint(1);
        this.tileGridPaint = new Paint(1);
        this.tileTintPaint = new Paint(1);
        this.ringPaint = new Paint(1);
        this.scopeFillPaint = new Paint(1);
        this.tickPaint = new Paint(1);
        this.sweepFillPaint = new Paint(1);
        this.sweepEdgePaint = new Paint(1);
        this.ripplePaint = new Paint(1);
        this.playerPaint = new Paint(1);
        this.playerHaloPaint = new Paint(1);
        this.nodePaint = new Paint(1);
        this.nodeCorePaint = new Paint(1);
        this.nodeRingPaint = new Paint(1);
        this.nodeTrailPaint = new Paint(1);
        this.nodePulsePaint = new Paint(1);
        this.captionPaint = new Paint(1);
        this.attributionPaint = new Paint(1);
        this.workingRect = new RectF();
        this.scopeClipPath = new Path();
        this.hasLocation = false;
        this.nodeActive = false;
        this.nodeLat = Double.NaN;
        this.nodeLon = Double.NaN;
        this.nodeId = "";
        this.tier = "none";
        this.hitsLeft = 0;
        this.hpTotal = 0;
        this.viewportMode = 0;
        this.zoomLevelOverride = -1;
        this.tilePlaceholderPaint.setStyle(Paint.Style.FILL);
        this.tilePlaceholderPaint.setColor(getColor(R.color.map_fill));
        this.tileGridPaint.setStyle(Paint.Style.STROKE);
        this.tileGridPaint.setStrokeWidth(dp(1.0f));
        this.tileGridPaint.setColor(getColor(R.color.map_line));
        this.tileGridPaint.setAlpha(90);
        this.tileTintPaint.setStyle(Paint.Style.FILL);
        this.tileTintPaint.setColor(403117082);
        this.ringPaint.setStyle(Paint.Style.STROKE);
        this.ringPaint.setStrokeWidth(dp(1.4f));
        this.ringPaint.setColor(getColor(R.color.glass_line));
        this.scopeFillPaint.setStyle(Paint.Style.FILL);
        this.scopeFillPaint.setColor(805901080);
        this.tickPaint.setStyle(Paint.Style.STROKE);
        this.tickPaint.setStrokeWidth(dp(1.0f));
        this.tickPaint.setColor(getColor(R.color.map_line));
        this.tickPaint.setAlpha(120);
        this.sweepFillPaint.setStyle(Paint.Style.FILL);
        this.sweepFillPaint.setColor(715059934);
        this.sweepEdgePaint.setStyle(Paint.Style.STROKE);
        this.sweepEdgePaint.setStrokeCap(Paint.Cap.ROUND);
        this.sweepEdgePaint.setStrokeWidth(dp(2.2f));
        this.sweepEdgePaint.setColor(getColor(R.color.glow));
        this.sweepEdgePaint.setAlpha(210);
        this.ripplePaint.setStyle(Paint.Style.STROKE);
        this.ripplePaint.setStrokeWidth(dp(2.2f));
        this.ripplePaint.setColor(getColor(R.color.glow));
        this.playerPaint.setStyle(Paint.Style.FILL);
        this.playerPaint.setColor(getColor(R.color.map_player));
        this.playerHaloPaint.setStyle(Paint.Style.STROKE);
        this.playerHaloPaint.setStrokeWidth(dp(2.6f));
        this.playerHaloPaint.setColor(getColor(R.color.glow));
        this.nodePaint.setStyle(Paint.Style.FILL);
        this.nodeCorePaint.setStyle(Paint.Style.FILL);
        this.nodeCorePaint.setColor(getColor(R.color.map_player));
        this.nodeRingPaint.setStyle(Paint.Style.STROKE);
        this.nodeRingPaint.setStrokeWidth(dp(2.4f));
        this.nodeTrailPaint.setStyle(Paint.Style.STROKE);
        this.nodeTrailPaint.setStrokeCap(Paint.Cap.ROUND);
        this.nodeTrailPaint.setStrokeWidth(dp(2.8f));
        this.nodePulsePaint.setStyle(Paint.Style.FILL);
        this.captionPaint.setColor(getColor(R.color.mist));
        this.captionPaint.setTextSize(dp(10.5f));
        this.captionPaint.setLetterSpacing(0.08f);
        this.attributionPaint.setColor(getColor(R.color.mist));
        this.attributionPaint.setTextSize(dp(9.0f));
        this.attributionPaint.setAlpha(185);
        this.diskCacheDir = new File(context.getCacheDir(), "opentopomap-tiles");
        if (!this.diskCacheDir.exists()) {
            this.diskCacheDir.mkdirs();
        }
    }

    public void setViewportMode(int i) {
        this.viewportMode = i;
        invalidate();
    }

    public void setZoomLevelOverride(int i) {
        if (i > 0) {
            i = Math.min(i, MAX_TILE_ZOOM);
        }
        this.zoomLevelOverride = i;
        invalidate();
    }

    public void setPlayerLocation(double d, double d2, double d3) {
        this.hasLocation = true;
        this.playerLat = d;
        this.playerLon = d2;
        this.playerAlt = d3;
        invalidate();
    }

    public void setNodeState(boolean z, String str, String str2, int i, int i2, double d, double d2) {
        this.nodeActive = z;
        if (str == null) {
            str = "";
        }
        this.nodeId = str;
        if (str2 == null) {
            str2 = "none";
        }
        this.tier = str2;
        this.hitsLeft = i;
        this.hpTotal = i2;
        this.nodeLat = d;
        this.nodeLon = d2;
        invalidate();
    }

    @Override // android.view.View
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        float width = getWidth();
        float height = getHeight();
        if (width > 0.0f && height > 0.0f) {
            if (!this.hasLocation) {
                drawFallbackMap(canvas, width, height);
                drawAttribution(canvas, width, height);
                return;
            }
            boolean zIsCompactMap = isCompactMap(width, height);
            int iResolveZoomLevel = resolveZoomLevel(width, height);
            double dLonToWorldX = lonToWorldX(this.playerLon, iResolveZoomLevel);
            double dLatToWorldY = latToWorldY(this.playerLat, iResolveZoomLevel);
            float f = width / 2.0f;
            float f2 = height / 2.0f;
            double d = f;
            Double.isNaN(d);
            float f3 = (float) (dLonToWorldX - d);
            double d2 = f2;
            Double.isNaN(d2);
            float f4 = (float) (dLatToWorldY - d2);
            drawVisibleTiles(canvas, iResolveZoomLevel, f3, f4, width, height);
            this.tileTintPaint.setAlpha(zIsCompactMap ? 62 : 12);
            canvas.drawRect(0.0f, 0.0f, width, height, this.tileTintPaint);
            drawRadarScope(canvas, width, height, f, f2, zIsCompactMap);
            drawNode(canvas, iResolveZoomLevel, f3, f4, f, f2);
            drawPlayer(canvas, f, f2, zIsCompactMap);
            drawCaption(canvas, width, height);
            drawAttribution(canvas, width, height);
            postInvalidateOnAnimation();
        }
    }

    private void drawVisibleTiles(Canvas canvas, int i, float f, float f2, float f3, float f4) {
        int i2 = 1 << i;
        int iFloor = (int) Math.floor(f / 256.0f);
        int iFloor2 = (int) Math.floor((f + f3) / 256.0f);
        int iFloor3 = (int) Math.floor((f2 + f4) / 256.0f);
        for (int iFloor4 = (int) Math.floor(f2 / 256.0f); iFloor4 <= iFloor3; iFloor4++) {
            for (int i3 = iFloor; i3 <= iFloor2; i3++) {
                float f5 = (i3 * TILE_SIZE) - f;
                float f6 = (iFloor4 * TILE_SIZE) - f2;
                this.workingRect.set(f5, f6, f5 + 256.0f, f6 + 256.0f);
                if (iFloor4 < 0 || iFloor4 >= i2) {
                    drawPlaceholderTile(canvas, this.workingRect);
                } else {
                    Bitmap bitmapLoadTileBitmap = loadTileBitmap(i, wrapTileX(i3, i2), iFloor4);
                    if (bitmapLoadTileBitmap == null) {
                        drawPlaceholderTile(canvas, this.workingRect);
                    } else {
                        canvas.drawBitmap(bitmapLoadTileBitmap, (Rect) null, this.workingRect, (Paint) null);
                    }
                }
            }
        }
    }

    private void drawPlaceholderTile(Canvas canvas, RectF rectF) {
        canvas.drawRect(rectF, this.tilePlaceholderPaint);
        canvas.drawLine(rectF.left, rectF.top, rectF.right, rectF.bottom, this.tileGridPaint);
        canvas.drawLine(rectF.left, rectF.bottom, rectF.right, rectF.top, this.tileGridPaint);
    }

    private void drawFallbackMap(Canvas canvas, float f, float f2) {
        canvas.drawRect(0.0f, 0.0f, f, f2, this.tilePlaceholderPaint);
        canvas.drawRect(0.0f, 0.0f, f, f2, this.tileTintPaint);
        float fMax = Math.max(dp(72.0f), Math.min(f, f2) / 4.0f);
        for (float f3 = 0.0f; f3 <= f; f3 += fMax) {
            canvas.drawLine(f3, 0.0f, f3, f2, this.tileGridPaint);
        }
        for (float f4 = 0.0f; f4 <= f2; f4 += fMax) {
            canvas.drawLine(0.0f, f4, f, f4, this.tileGridPaint);
        }
    }

    private void drawRadarScope(Canvas canvas, float f, float f2, float f3, float f4, boolean z) {
        long jCurrentTimeMillis = System.currentTimeMillis();
        if (z) {
            float fMin = Math.min(f, f2) * 0.44f;
            float f5 = fMin / 3.0f;
            this.scopeFillPaint.setAlpha(34);
            canvas.drawCircle(f3, f4, fMin, this.scopeFillPaint);
            this.ringPaint.setStrokeWidth(dp(1.5f));
            this.ringPaint.setAlpha(96);
            canvas.drawCircle(f3, f4, fMin, this.ringPaint);
            int iSave = canvas.save();
            this.scopeClipPath.reset();
            this.scopeClipPath.addCircle(f3, f4, fMin, Path.Direction.CW);
            canvas.clipPath(this.scopeClipPath);
            float f6 = ((jCurrentTimeMillis % 3200) / 3200.0f) * 360.0f;
            float f7 = f3 - fMin;
            float f8 = f4 - fMin;
            float f9 = f3 + fMin;
            float f10 = f4 + fMin;
            this.workingRect.set(f7, f8, f9, f10);
            this.sweepFillPaint.setAlpha(86);
            this.sweepEdgePaint.setAlpha(210);
            canvas.drawArc(this.workingRect, f6 - 20.0f, 20.0f, true, this.sweepFillPaint);
            canvas.drawArc(this.workingRect, f6 - 1.8f, 1.8f, false, this.sweepEdgePaint);
            canvas.restoreToCount(iSave);
            this.ringPaint.setAlpha(78);
            for (int i = 1; i <= 3; i++) {
                canvas.drawCircle(f3, f4, i * f5, this.ringPaint);
            }
            this.tickPaint.setAlpha(126);
            canvas.drawLine(f7, f4, f9, f4, this.tickPaint);
            canvas.drawLine(f3, f8, f3, f10, this.tickPaint);
            return;
        }
        float fHypot = ((float) Math.hypot(f, f2)) * 0.58f;
        this.scopeFillPaint.setAlpha(18);
        canvas.drawCircle(f3, f4, fHypot, this.scopeFillPaint);
        this.ringPaint.setAlpha(72);
        this.ringPaint.setStrokeWidth(dp(1.6f));
        canvas.drawCircle(f3, f4, fHypot, this.ringPaint);
        this.ringPaint.setAlpha(54);
        canvas.drawCircle(f3, f4, 0.72f * fHypot, this.ringPaint);
        this.tickPaint.setAlpha(96);
        float f11 = f3 - fHypot;
        float f12 = f3 + fHypot;
        canvas.drawLine(f11, f4, f12, f4, this.tickPaint);
        float f13 = f4 - fHypot;
        float f14 = f4 + fHypot;
        canvas.drawLine(f3, f13, f3, f14, this.tickPaint);
        int iSave2 = canvas.save();
        this.scopeClipPath.reset();
        this.scopeClipPath.addCircle(f3, f4, fHypot, Path.Direction.CW);
        canvas.clipPath(this.scopeClipPath);
        float f15 = ((jCurrentTimeMillis % 4200) / 4200.0f) * 360.0f;
        this.workingRect.set(f11, f13, f12, f14);
        this.sweepFillPaint.setAlpha(38);
        this.sweepEdgePaint.setAlpha(184);
        canvas.drawArc(this.workingRect, f15 - 14.0f, 14.0f, true, this.sweepFillPaint);
        canvas.drawArc(this.workingRect, f15 - 0.9f, 0.9f, false, this.sweepEdgePaint);
        canvas.restoreToCount(iSave2);
    }

    private void drawPlayer(Canvas canvas, float f, float f2, boolean z) {
        float fLerp;
        if (!this.hasLocation) {
            return;
        }
        long jCurrentTimeMillis = System.currentTimeMillis();
        float fDp = dp(z ? 10.0f : 11.0f);
        for (int i = 0; i < 3; i++) {
            float f3 = (((jCurrentTimeMillis % 2400) / 2400.0f) + (i / 3.0f)) % 1.0f;
            float f4 = f3 * f3 * (3.0f - (2.0f * f3));
            if (z) {
                fLerp = lerp(dp(14.0f), dp(58.0f), f4);
            } else {
                fLerp = lerp(dp(18.0f), dp(128.0f), f4);
            }
            float f5 = 1.0f - f3;
            this.ripplePaint.setAlpha((int) ((z ? 108 : 96) * f5 * f5));
            canvas.drawCircle(f, f2, fLerp, this.ripplePaint);
        }
        if (z) {
            this.playerHaloPaint.setAlpha(192);
            canvas.drawCircle(f, f2, dp(20.0f), this.playerHaloPaint);
        }
        canvas.drawCircle(f, f2, fDp, this.playerPaint);
    }

    private void drawNode(Canvas canvas, int i, float f, float f2, float f3, float f4) {
        if (!this.nodeActive || Double.isNaN(this.nodeLat) || Double.isNaN(this.nodeLon)) {
            return;
        }
        boolean zIsCompactMap = isCompactMap(getWidth(), getHeight());
        long jCurrentTimeMillis = System.currentTimeMillis();
        double dLonToWorldX = lonToWorldX(this.nodeLon, i);
        double d = f;
        Double.isNaN(d);
        float f5 = (float) (dLonToWorldX - d);
        double dLatToWorldY = latToWorldY(this.nodeLat, i);
        double d2 = f2;
        Double.isNaN(d2);
        float f6 = (float) (dLatToWorldY - d2);
        float fDp = dp(zIsCompactMap ? 11.0f : 13.0f);
        float fDp2 = dp(10.0f) + fDp;
        float fDp3 = dp(zIsCompactMap ? 28.0f : 188.0f) + fDp;
        float fClamp = clamp(f5, fDp2, getWidth() - fDp2);
        float fClamp2 = clamp(f6, fDp2, getHeight() - fDp3);
        int iTierColor = tierColor(this.tier);
        float fDp4 = dp(zIsCompactMap ? 6.0f : 9.0f) + fDp + (((((float) Math.sin(jCurrentTimeMillis * 0.0042f)) * 0.5f) + 0.5f) * dp(zIsCompactMap ? 6.0f : 10.0f));
        this.nodeTrailPaint.setColor(iTierColor);
        this.nodeTrailPaint.setAlpha(zIsCompactMap ? 210 : 176);
        canvas.drawLine(f3, f4, fClamp, fClamp2, this.nodeTrailPaint);
        this.nodePulsePaint.setColor(iTierColor);
        this.nodePulsePaint.setAlpha(zIsCompactMap ? 72 : 58);
        canvas.drawCircle(fClamp, fClamp2, fDp4, this.nodePulsePaint);
        this.nodePaint.setColor(iTierColor);
        this.nodeRingPaint.setColor(iTierColor);
        this.nodeRingPaint.setAlpha(226);
        canvas.drawCircle(fClamp, fClamp2, fDp, this.nodePaint);
        canvas.drawCircle(fClamp, fClamp2, dp(5.0f) + fDp, this.nodeRingPaint);
        canvas.drawCircle(fClamp, fClamp2, 0.42f * fDp, this.nodeCorePaint);
        if (this.hpTotal > 0) {
            this.workingRect.set((fClamp - fDp) - dp(8.0f), (fClamp2 - fDp) - dp(8.0f), fClamp + fDp + dp(8.0f), fClamp2 + fDp + dp(8.0f));
            this.nodeRingPaint.setAlpha(255);
            canvas.drawArc(this.workingRect, -90.0f, 360.0f * (1.0f - (this.hitsLeft / this.hpTotal)), false, this.nodeRingPaint);
        }
    }

    private void drawCaption(Canvas canvas, float f, float f2) {
        String str;
        if (this.nodeActive && !Double.isNaN(this.nodeLat) && !Double.isNaN(this.nodeLon)) {
            str = String.format(Locale.US, "%s · %d м", tierLabel(this.tier), Long.valueOf(Math.round(distanceMeters(this.playerLat, this.playerLon, this.nodeLat, this.nodeLon))));
        } else {
            str = String.format(Locale.US, "%s %.4f · %s %.4f · %.0f м", this.playerLat >= 0.0d ? "С" : "Ю", Double.valueOf(Math.abs(this.playerLat)), this.playerLon >= 0.0d ? "В" : "З", Double.valueOf(Math.abs(this.playerLon)), Double.valueOf(this.playerAlt));
        }
        float fMeasureText = this.captionPaint.measureText(str);
        float fDp = f2 - dp(isCompactMap(f, f2) ? 10.0f : 148.0f);
        this.captionPaint.setAlpha(120);
        float f3 = (f / 2.0f) - (fMeasureText / 2.0f);
        canvas.drawText(str, f3, dp(1.5f) + fDp, this.captionPaint);
        this.captionPaint.setAlpha(228);
        canvas.drawText(str, f3, fDp, this.captionPaint);
    }

    private void drawAttribution(Canvas canvas, float f, float f2) {
        canvas.drawText("Данные карты © OpenTopoMap, OpenStreetMap", dp(12.0f), f2 - dp(isCompactMap(f, f2) ? 26.0f : 164.0f), this.attributionPaint);
    }

    private Bitmap loadTileBitmap(int i, int i2, int i3) {
        String str = i + "_" + i2 + "_" + i3;
        Bitmap bitmap = MEMORY_CACHE.get(str);
        if (bitmap != null && !bitmap.isRecycled()) {
            return bitmap;
        }
        File file = new File(this.diskCacheDir, str + ".png");
        if (file.isFile()) {
            Bitmap bitmapDecodeFile = BitmapFactory.decodeFile(file.getAbsolutePath());
            if (bitmapDecodeFile != null) {
                MEMORY_CACHE.put(str, bitmapDecodeFile);
                return bitmapDecodeFile;
            }
            file.delete();
        }
        queueTileFetch(str, i, i2, i3, file);
        return null;
    }

    private void queueTileFetch(final String str, final int i, final int i2, final int i3, final File file) {
        if (!IN_FLIGHT.add(str)) {
            return;
        }
        TILE_EXECUTOR.execute(new Runnable() { // from class: io.peakmood.mobile.WorldMapView.2
            @Override // java.lang.Runnable
            public void run() {
                try {
                    try {
                        WorldMapView.this.downloadTile(i, i2, i3, file);
                        Bitmap bitmapDecodeFile = BitmapFactory.decodeFile(file.getAbsolutePath());
                        if (bitmapDecodeFile != null) {
                            WorldMapView.MEMORY_CACHE.put(str, bitmapDecodeFile);
                        }
                    } catch (Exception e) {
                        Log.w(WorldMapView.TAG, "Tile fetch failed for " + str, e);
                    }
                } finally {
                    WorldMapView.IN_FLIGHT.remove(str);
                    WorldMapView.this.postInvalidateOnAnimation();
                }
            }
        });
    }

    /* JADX INFO: Access modifiers changed from: private */
    public void downloadTile(int i, int i2, int i3, File file) throws Exception {
        String str = TILE_HOSTS[WorldMapView$$ExternalSyntheticBackport0.m(i2 + i3, TILE_HOSTS.length)];
        String[] strArr = TILE_SCHEMES;
        int length = strArr.length;
        Exception e = null;
        int i4 = 0;
        while (i4 < length) {
            String str2 = strArr[i4];
            int i5 = i;
            int i6 = i2;
            int i7 = i3;
            File file2 = file;
            try {
                downloadTileWithScheme(str2, str, i5, i6, i7, file2);
                return;
            } catch (Exception e2) {
                e = e2;
                Log.w(TAG, "Tile fetch via " + str2 + " failed for " + str + "/" + i5 + "/" + i6 + "/" + i7, e);
                i4++;
                i = i5;
                i2 = i6;
                i3 = i7;
                file = file2;
            }
        }
        if (e != null) {
            throw e;
        }
        throw new IOException("Tile fetch failed without exception");
    }

    /* JADX WARN: Removed duplicated region for block: B:41:0x0087 A[EXC_TOP_SPLITTER, SYNTHETIC] */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private void downloadTileWithScheme(java.lang.String r5, java.lang.String r6, int r7, int r8, int r9, java.io.File r10) throws java.lang.Exception {
        /*
            r4 = this;
            java.net.URL r0 = new java.net.URL
            java.util.Locale r1 = java.util.Locale.US
            java.lang.Integer r7 = java.lang.Integer.valueOf(r7)
            java.lang.Integer r8 = java.lang.Integer.valueOf(r8)
            java.lang.Integer r9 = java.lang.Integer.valueOf(r9)
            r2 = 5
            java.lang.Object[] r2 = new java.lang.Object[r2]
            r3 = 0
            r2[r3] = r5
            r5 = 1
            r2[r5] = r6
            r6 = 2
            r2[r6] = r7
            r6 = 3
            r2[r6] = r8
            r6 = 4
            r2[r6] = r9
            java.lang.String r6 = "%s://%s/%d/%d/%d.png"
            java.lang.String r6 = java.lang.String.format(r1, r6, r2)
            r0.<init>(r6)
            java.net.URLConnection r6 = r0.openConnection()
            java.net.HttpURLConnection r6 = (java.net.HttpURLConnection) r6
            r7 = 6000(0x1770, float:8.408E-42)
            r6.setConnectTimeout(r7)
            r6.setReadTimeout(r7)
            r6.setUseCaches(r5)
            java.lang.String r5 = "Accept"
            java.lang.String r7 = "image/png"
            r6.setRequestProperty(r5, r7)
            java.lang.String r5 = "User-Agent"
            java.lang.String r7 = "PeakMood/1.0 (Android)"
            r6.setRequestProperty(r5, r7)
            int r5 = r6.getResponseCode()     // Catch: java.lang.Throwable -> Lb3
            r7 = 200(0xc8, float:2.8E-43)
            if (r5 != r7) goto L90
            java.io.InputStream r5 = r6.getInputStream()     // Catch: java.lang.Throwable -> Lb3
            java.io.FileOutputStream r7 = new java.io.FileOutputStream     // Catch: java.lang.Throwable -> L84
            r7.<init>(r10)     // Catch: java.lang.Throwable -> L84
            r8 = 8192(0x2000, float:1.148E-41)
            byte[] r8 = new byte[r8]     // Catch: java.lang.Throwable -> L7a
        L5f:
            int r9 = r5.read(r8)     // Catch: java.lang.Throwable -> L7a
            r10 = -1
            if (r9 == r10) goto L6a
            r7.write(r8, r3, r9)     // Catch: java.lang.Throwable -> L7a
            goto L5f
        L6a:
            r7.flush()     // Catch: java.lang.Throwable -> L7a
            r7.close()     // Catch: java.lang.Throwable -> L84
            if (r5 == 0) goto L75
            r5.close()     // Catch: java.lang.Throwable -> Lb3
        L75:
            r6.disconnect()
            return
        L7a:
            r8 = move-exception
            r7.close()     // Catch: java.lang.Throwable -> L7f
            goto L83
        L7f:
            r7 = move-exception
            io.peakmood.mobile.MainActivity$$ExternalSyntheticBackport0.m(r8, r7)     // Catch: java.lang.Throwable -> L84
        L83:
            throw r8     // Catch: java.lang.Throwable -> L84
        L84:
            r7 = move-exception
            if (r5 == 0) goto L8f
            r5.close()     // Catch: java.lang.Throwable -> L8b
            goto L8f
        L8b:
            r5 = move-exception
            io.peakmood.mobile.MainActivity$$ExternalSyntheticBackport0.m(r7, r5)     // Catch: java.lang.Throwable -> Lb3
        L8f:
            throw r7     // Catch: java.lang.Throwable -> Lb3
        L90:
            java.io.IOException r7 = new java.io.IOException     // Catch: java.lang.Throwable -> Lb3
            java.lang.StringBuilder r8 = new java.lang.StringBuilder     // Catch: java.lang.Throwable -> Lb3
            r8.<init>()     // Catch: java.lang.Throwable -> Lb3
            java.lang.String r9 = "Unexpected HTTP "
            java.lang.StringBuilder r8 = r8.append(r9)     // Catch: java.lang.Throwable -> Lb3
            java.lang.StringBuilder r5 = r8.append(r5)     // Catch: java.lang.Throwable -> Lb3
            java.lang.String r8 = " for "
            java.lang.StringBuilder r5 = r5.append(r8)     // Catch: java.lang.Throwable -> Lb3
            java.lang.StringBuilder r5 = r5.append(r0)     // Catch: java.lang.Throwable -> Lb3
            java.lang.String r5 = r5.toString()     // Catch: java.lang.Throwable -> Lb3
            r7.<init>(r5)     // Catch: java.lang.Throwable -> Lb3
            throw r7     // Catch: java.lang.Throwable -> Lb3
        Lb3:
            r5 = move-exception
            r6.disconnect()
            goto Lb9
        Lb8:
            throw r5
        Lb9:
            goto Lb8
        */
        throw new UnsupportedOperationException("Method not decompiled: io.peakmood.mobile.WorldMapView.downloadTileWithScheme(java.lang.String, java.lang.String, int, int, int, java.io.File):void");
    }

    private int resolveZoomLevel(float f, float f2) {
        if (this.zoomLevelOverride > 0) {
            return Math.min(this.zoomLevelOverride, MAX_TILE_ZOOM);
        }
        float fMin = Math.min(f, f2) / getResources().getDisplayMetrics().density;
        return (fMin >= 180.0f && fMin < 320.0f) ? MAX_TILE_ZOOM : MAX_TILE_ZOOM;
    }

    private boolean isCompactMap(float f, float f2) {
        if (this.viewportMode == 2) {
            return true;
        }
        return this.viewportMode != 1 && Math.min(f, f2) / getResources().getDisplayMetrics().density < 220.0f;
    }

    private double lonToWorldX(double d, int i) {
        double d2 = 1 << i;
        Double.isNaN(d2);
        return ((d + 180.0d) / 360.0d) * d2 * 256.0d;
    }

    private double latToWorldY(double d, int i) {
        double d2 = 1 << i;
        double dLog = (1.0d - (Math.log(Math.tan((Math.toRadians(Math.max(-85.05112878d, Math.min(85.05112878d, d))) / 2.0d) + 0.7853981633974483d)) / 3.141592653589793d)) / 2.0d;
        Double.isNaN(d2);
        return dLog * d2 * 256.0d;
    }

    private int wrapTileX(int i, int i2) {
        int i3 = i % i2;
        if (i3 < 0) {
            return i3 + i2;
        }
        return i3;
    }

    private float lerp(float f, float f2, float f3) {
        return f + ((f2 - f) * f3);
    }

    private float clamp(float f, float f2, float f3) {
        return Math.max(f2, Math.min(f3, f));
    }

    private String tierLabel(String str) {
        if ("common".equals(str)) {
            return "Обычная находка";
        }
        if ("rare".equals(str)) {
            return "Редкая находка";
        }
        if ("epic".equals(str)) {
            return "Эпическая находка";
        }
        if ("FLAG".equals(str)) {
            return "Мифическая находка";
        }
        return "Сканируем местность...";
    }

    private double distanceMeters(double d, double d2, double d3, double d4) {
        double radians = Math.toRadians(d);
        double radians2 = Math.toRadians(d3);
        double radians3 = Math.toRadians(d3 - d);
        double d5 = radians3 / 2.0d;
        double radians4 = Math.toRadians(d4 - d2) / 2.0d;
        double dSin = (Math.sin(d5) * Math.sin(d5)) + (Math.cos(radians) * Math.cos(radians2) * Math.sin(radians4) * Math.sin(radians4));
        return 1.2742E7d * Math.atan2(Math.sqrt(dSin), Math.sqrt(1.0d - dSin));
    }

    private int tierColor(String str) {
        if ("common".equals(str)) {
            return getColor(R.color.map_node_common);
        }
        if ("rare".equals(str)) {
            return getColor(R.color.map_node_rare);
        }
        if ("epic".equals(str)) {
            return getColor(R.color.map_node_epic);
        }
        if ("FLAG".equals(str)) {
            return getColor(R.color.map_node_mythic);
        }
        return getColor(R.color.map_line);
    }

    private int getColor(int i) {
        return getResources().getColor(i);
    }

    private float dp(float f) {
        return f * getResources().getDisplayMetrics().density;
    }
}
