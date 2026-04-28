package io.peakmood.mobile;

import android.content.Context;
import android.content.res.Resources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/* JADX INFO: loaded from: classes.dex */
public final class TerrainModel {
    private static final double BUCKET_STEP_DEGREES = 6.0d;
    private static final int GLOBAL_RELIEF_HEIGHT = 1440;
    private static final int GLOBAL_RELIEF_STEP_MILLI_M = 81063;
    private static final int GLOBAL_RELIEF_WIDTH = 2880;
    private static final int GLOBAL_RELIEF_ZERO = 128;
    private static final int LAT_BUCKET_COUNT = 30;
    private static final int LON_BUCKET_COUNT = 60;
    private static volatile TerrainModel instance;
    private final Map<Long, List<ReliefAnchor>> anchorIndex;
    private final List<ReliefAnchor> anchors;
    private final Bitmap globalReliefBitmap;

    public static TerrainModel getInstance(Context context) {
        TerrainModel terrainModel;
        TerrainModel terrainModel2 = instance;
        if (terrainModel2 != null) {
            return terrainModel2;
        }
        synchronized (TerrainModel.class) {
            if (instance == null) {
                instance = new TerrainModel(context.getApplicationContext());
            }
            terrainModel = instance;
        }
        return terrainModel;
    }

    private TerrainModel(Context context) throws IllegalAccessException, InvocationTargetException {
        ArrayList arrayList = new ArrayList();
        loadSpecialAnchors(context.getResources(), arrayList);
        this.anchors = Collections.unmodifiableList(arrayList);
        this.anchorIndex = buildAnchorIndex(arrayList);
        this.globalReliefBitmap = loadGlobalReliefBitmap(context.getResources());
    }

    public TerrainSnapshot snapshot(double d, double d2, double d3) {
        String str;
        AnchorMatch anchorMatchNearestAnchor = nearestAnchor(d, d2);
        int iGlobalReliefElevationM = globalReliefElevationM(d, d2);
        if (anchorMatchNearestAnchor.anchor != null && anchorMatchNearestAnchor.distanceKm <= anchorMatchNearestAnchor.anchor.radiusKm) {
            iGlobalReliefElevationM = anchorMatchNearestAnchor.anchor.elevationM;
            str = anchorMatchNearestAnchor.anchor.name;
        } else {
            str = "Global Relief Cache";
        }
        return new TerrainSnapshot(str, iGlobalReliefElevationM);
    }

    private AnchorMatch nearestAnchor(double d, double d2) {
        BucketCoordinate bucketCoordinate = bucketCoordinate(d, d2);
        ReliefAnchor reliefAnchor = null;
        double d3 = Double.POSITIVE_INFINITY;
        for (int i = -1; i <= 1; i++) {
            int i2 = bucketCoordinate.latIndex + i;
            if (i2 >= 0 && i2 < LAT_BUCKET_COUNT) {
                for (int i3 = -1; i3 <= 1; i3++) {
                    List<ReliefAnchor> list = this.anchorIndex.get(Long.valueOf(bucketKey(i2, ((bucketCoordinate.lonIndex + i3) + LON_BUCKET_COUNT) % LON_BUCKET_COUNT)));
                    if (list != null) {
                        for (ReliefAnchor reliefAnchor2 : list) {
                            double dHaversineKm = haversineKm(d, d2, reliefAnchor2.lat, reliefAnchor2.lon);
                            if (dHaversineKm < d3) {
                                reliefAnchor = reliefAnchor2;
                                d3 = dHaversineKm;
                            }
                        }
                    }
                }
            }
        }
        if (reliefAnchor != null) {
            return new AnchorMatch(reliefAnchor, d3);
        }
        for (ReliefAnchor reliefAnchor3 : this.anchors) {
            double dHaversineKm2 = haversineKm(d, d2, reliefAnchor3.lat, reliefAnchor3.lon);
            if (dHaversineKm2 < d3) {
                reliefAnchor = reliefAnchor3;
                d3 = dHaversineKm2;
            }
        }
        return new AnchorMatch(reliefAnchor, d3);
    }

    /* JADX WARN: Code restructure failed: missing block: B:16:0x0092, code lost:
    
        throw new java.lang.IllegalStateException("Bad terrain row on line " + r2);
     */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    private void loadSpecialAnchors(android.content.res.Resources r17, java.util.List<io.peakmood.mobile.TerrainModel.ReliefAnchor> r18) throws java.lang.IllegalAccessException, java.lang.reflect.InvocationTargetException {
        /*
            r16 = this;
            r0 = 2130968577(0x7f040001, float:1.7545812E38)
            r1 = r17
            java.io.InputStream r0 = r1.openRawResource(r0)
            java.io.BufferedReader r1 = new java.io.BufferedReader     // Catch: java.io.IOException -> La6
            java.io.InputStreamReader r2 = new java.io.InputStreamReader     // Catch: java.io.IOException -> La6
            java.nio.charset.Charset r3 = java.nio.charset.StandardCharsets.UTF_8     // Catch: java.io.IOException -> La6
            r2.<init>(r0, r3)     // Catch: java.io.IOException -> La6
            r1.<init>(r2)     // Catch: java.io.IOException -> La6
            r0 = 0
            r2 = 0
        L17:
            java.lang.String r3 = r1.readLine()     // Catch: java.lang.Throwable -> L9b
            if (r3 == 0) goto L96
            r4 = 1
            int r2 = r2 + r4
            java.lang.String r3 = r3.trim()     // Catch: java.lang.Throwable -> L9b
            boolean r5 = r3.isEmpty()     // Catch: java.lang.Throwable -> L9b
            if (r5 != 0) goto L93
            java.lang.String r5 = "#"
            boolean r5 = r3.startsWith(r5)     // Catch: java.lang.Throwable -> L9b
            if (r5 == 0) goto L34
            r3 = r18
            goto L17
        L34:
            java.lang.String r5 = "\\|"
            java.lang.String[] r3 = r3.split(r5)     // Catch: java.lang.Throwable -> L9b
            int r5 = r3.length     // Catch: java.lang.Throwable -> L9b
            r6 = 5
            if (r5 != r6) goto L7a
            io.peakmood.mobile.TerrainModel$ReliefAnchor r7 = new io.peakmood.mobile.TerrainModel$ReliefAnchor     // Catch: java.lang.Throwable -> L9b
            r5 = r3[r0]     // Catch: java.lang.Throwable -> L9b
            java.lang.String r8 = r5.trim()     // Catch: java.lang.Throwable -> L9b
            r4 = r3[r4]     // Catch: java.lang.Throwable -> L9b
            java.lang.String r4 = r4.trim()     // Catch: java.lang.Throwable -> L9b
            double r9 = java.lang.Double.parseDouble(r4)     // Catch: java.lang.Throwable -> L9b
            r4 = 2
            r4 = r3[r4]     // Catch: java.lang.Throwable -> L9b
            java.lang.String r4 = r4.trim()     // Catch: java.lang.Throwable -> L9b
            double r11 = java.lang.Double.parseDouble(r4)     // Catch: java.lang.Throwable -> L9b
            r4 = 3
            r4 = r3[r4]     // Catch: java.lang.Throwable -> L9b
            java.lang.String r4 = r4.trim()     // Catch: java.lang.Throwable -> L9b
            int r13 = java.lang.Integer.parseInt(r4)     // Catch: java.lang.Throwable -> L9b
            r4 = 4
            r3 = r3[r4]     // Catch: java.lang.Throwable -> L9b
            java.lang.String r3 = r3.trim()     // Catch: java.lang.Throwable -> L9b
            double r14 = java.lang.Double.parseDouble(r3)     // Catch: java.lang.Throwable -> L9b
            r7.<init>(r8, r9, r11, r13, r14)     // Catch: java.lang.Throwable -> L9b
            r3 = r18
            r3.add(r7)     // Catch: java.lang.Throwable -> L9b
            goto L17
        L7a:
            java.lang.IllegalStateException r0 = new java.lang.IllegalStateException     // Catch: java.lang.Throwable -> L9b
            java.lang.StringBuilder r3 = new java.lang.StringBuilder     // Catch: java.lang.Throwable -> L9b
            r3.<init>()     // Catch: java.lang.Throwable -> L9b
            java.lang.String r4 = "Bad terrain row on line "
            java.lang.StringBuilder r3 = r3.append(r4)     // Catch: java.lang.Throwable -> L9b
            java.lang.StringBuilder r2 = r3.append(r2)     // Catch: java.lang.Throwable -> L9b
            java.lang.String r2 = r2.toString()     // Catch: java.lang.Throwable -> L9b
            r0.<init>(r2)     // Catch: java.lang.Throwable -> L9b
            throw r0     // Catch: java.lang.Throwable -> L9b
        L93:
            r3 = r18
            goto L17
        L96:
            r1.close()     // Catch: java.io.IOException -> La6
            return
        L9b:
            r0 = move-exception
            r2 = r0
            r1.close()     // Catch: java.lang.Throwable -> La1
            goto La5
        La1:
            r0 = move-exception
            io.peakmood.mobile.MainActivity$$ExternalSyntheticBackport0.m(r2, r0)     // Catch: java.io.IOException -> La6
        La5:
            throw r2     // Catch: java.io.IOException -> La6
        La6:
            r0 = move-exception
            java.lang.IllegalStateException r1 = new java.lang.IllegalStateException
            java.lang.String r2 = "Unable to load terrain anchors"
            r1.<init>(r2, r0)
            goto Lb0
        Laf:
            throw r1
        Lb0:
            goto Laf
        */
        throw new UnsupportedOperationException("Method not decompiled: io.peakmood.mobile.TerrainModel.loadSpecialAnchors(android.content.res.Resources, java.util.List):void");
    }

    private Bitmap loadGlobalReliefBitmap(Resources resources) throws IllegalAccessException, InvocationTargetException {
        BitmapFactory.Options options = new BitmapFactory.Options();
        options.inScaled = false;
        try {
            InputStream inputStreamOpenRawResource = resources.openRawResource(R.raw.global_relief);
            try {
                Bitmap bitmapDecodeStream = BitmapFactory.decodeStream(inputStreamOpenRawResource, null, options);
                if (inputStreamOpenRawResource != null) {
                    inputStreamOpenRawResource.close();
                }
                if (bitmapDecodeStream == null) {
                    throw new IllegalStateException("Unable to decode global relief map");
                }
                if (bitmapDecodeStream.getWidth() != GLOBAL_RELIEF_WIDTH || bitmapDecodeStream.getHeight() != GLOBAL_RELIEF_HEIGHT) {
                    throw new IllegalStateException("Unexpected global relief dimensions: " + bitmapDecodeStream.getWidth() + "x" + bitmapDecodeStream.getHeight());
                }
                return bitmapDecodeStream;
            } finally {
            }
        } catch (IOException e) {
            throw new IllegalStateException("Unable to load global relief map", e);
        }
    }

    private Map<Long, List<ReliefAnchor>> buildAnchorIndex(List<ReliefAnchor> list) {
        HashMap map = new HashMap();
        for (ReliefAnchor reliefAnchor : list) {
            BucketCoordinate bucketCoordinate = bucketCoordinate(reliefAnchor.lat, reliefAnchor.lon);
            long jBucketKey = bucketKey(bucketCoordinate.latIndex, bucketCoordinate.lonIndex);
            List arrayList = (List) map.get(Long.valueOf(jBucketKey));
            if (arrayList == null) {
                arrayList = new ArrayList();
                map.put(Long.valueOf(jBucketKey), arrayList);
            }
            arrayList.add(reliefAnchor);
        }
        return map;
    }

    private static BucketCoordinate bucketCoordinate(double d, double d2) {
        double dMax = Math.max(-89.999999d, Math.min(89.999999d, d));
        double dNormalizeLon = normalizeLon(d2);
        return new BucketCoordinate(Math.max(0, Math.min(29, (int) Math.floor((dMax + 90.0d) / BUCKET_STEP_DEGREES))), ((((int) Math.floor((dNormalizeLon + 180.0d) / BUCKET_STEP_DEGREES)) % LON_BUCKET_COUNT) + LON_BUCKET_COUNT) % LON_BUCKET_COUNT);
    }

    private static double normalizeLon(double d) {
        double d2 = ((((d + 180.0d) % 360.0d) + 360.0d) % 360.0d) - 180.0d;
        if (d2 == -180.0d && d > 0.0d) {
            return 180.0d;
        }
        return d2;
    }

    private static long bucketKey(int i, int i2) {
        return (((long) i2) & 4294967295L) ^ (((long) i) << 32);
    }

    private int globalReliefElevationM(double d, double d2) {
        double dNormalizeLon = normalizeLon(d2);
        if (dNormalizeLon == 180.0d) {
            dNormalizeLon = -180.0d;
        }
        double d3 = 1439.0d;
        double d4 = ((90.0d - d) / 180.0d) * 1439.0d;
        double d5 = ((dNormalizeLon + 180.0d) / 360.0d) * 2880.0d;
        if (d4 < 0.0d) {
            d3 = 0.0d;
        } else if (d4 <= 1439.0d) {
            d3 = d4;
        }
        int iFloor = (int) Math.floor(d3);
        int iMin = Math.min(iFloor + 1, 1439);
        int iFloor2 = ((int) Math.floor(d5)) % GLOBAL_RELIEF_WIDTH;
        if (iFloor2 < 0) {
            iFloor2 += GLOBAL_RELIEF_WIDTH;
        }
        int i = (iFloor2 + 1) % GLOBAL_RELIEF_WIDTH;
        double d6 = iFloor;
        Double.isNaN(d6);
        double d7 = d3 - d6;
        double dFloor = d5 - Math.floor(d5);
        return roundMilliMetersToMeters((int) Math.round((lerp(lerp(this.globalReliefBitmap.getPixel(iFloor2, iFloor) & 255, this.globalReliefBitmap.getPixel(i, iFloor) & 255, dFloor), lerp(this.globalReliefBitmap.getPixel(iFloor2, iMin) & 255, this.globalReliefBitmap.getPixel(i, iMin) & 255, dFloor), d7) - 128.0d) * 81063.0d));
    }

    private static int roundMilliMetersToMeters(int i) {
        if (i >= 0) {
            return (i + 500) / 1000;
        }
        return -(((-i) + 500) / 1000);
    }

    private static double lerp(double d, double d2, double d3) {
        return d + ((d2 - d) * d3);
    }

    private static double haversineKm(double d, double d2, double d3, double d4) {
        double radians = Math.toRadians(d);
        double radians2 = Math.toRadians(d3);
        double radians3 = Math.toRadians(d3 - d);
        double d5 = radians3 / 2.0d;
        double radians4 = Math.toRadians(d4 - d2) / 2.0d;
        double dSin = (Math.sin(d5) * Math.sin(d5)) + (Math.cos(radians) * Math.cos(radians2) * Math.sin(radians4) * Math.sin(radians4));
        return 12742.0d * Math.atan2(Math.sqrt(dSin), Math.sqrt(1.0d - dSin));
    }

    private static final class ReliefAnchor {
        final int elevationM;
        final double lat;
        final double lon;
        final String name;
        final double radiusKm;

        ReliefAnchor(String str, double d, double d2, int i, double d3) {
            this.name = str;
            this.lat = d;
            this.lon = d2;
            this.elevationM = i;
            this.radiusKm = d3;
        }
    }

    private static final class AnchorMatch {
        final ReliefAnchor anchor;
        final double distanceKm;

        AnchorMatch(ReliefAnchor reliefAnchor, double d) {
            this.anchor = reliefAnchor;
            this.distanceKm = d;
        }
    }

    private static final class BucketCoordinate {
        final int latIndex;
        final int lonIndex;

        BucketCoordinate(int i, int i2) {
            this.latIndex = i;
            this.lonIndex = i2;
        }
    }

    public static final class TerrainSnapshot {
        public final int expectedElevationM;
        public final String label;

        TerrainSnapshot(String str, int i) {
            this.label = str;
            this.expectedElevationM = i;
        }
    }
}
