import 'dotenv/config';
import { Telegraf, Markup } from 'telegraf';
import fetch from 'node-fetch';
import XLSX from 'xlsx';
import fs from 'fs';

// --- ENV ---
const {
  BOT_TOKEN,
  ADMIN_ID,
  GITHUB_RAW_BASE,
  INVENTORY_FILE,
  BRAND_FILES,
  ABOUT_TEXT,
  CONTACT_TEXT,
  SPECIAL_OFFER_TEXT
} = process.env;

if (!BOT_TOKEN  !ADMIN_ID  !GITHUB_RAW_BASE  !INVENTORY_FILE  !BRAND_FILES) {
  console.error('Missing env config: BOT_TOKEN, ADMIN_ID, GITHUB_RAW_BASE, INVENTORY_FILE, BRAND_FILES are required');
  process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN);

// --- Persistence (JSON files) ---
const DATA_DIR = './data';
const MEMBERS_FILE = ${DATA_DIR}/members.json;   // approved members
const ORDERS_FILE = ${DATA_DIR}/orders.json;     // submitted orders

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);
if (!fs.existsSync(MEMBERS_FILE)) fs.writeFileSync(MEMBERS_FILE, JSON.stringify({ members: [] }, null, 2));
if (!fs.existsSync(ORDERS_FILE)) fs.writeFileSync(ORDERS_FILE, JSON.stringify({ orders: [] }, null, 2));

const readJSON = (path) => JSON.parse(fs.readFileSync(path, 'utf-8'));
const writeJSON = (path, obj) => fs.writeFileSync(path, JSON.stringify(obj, null, 2));

// --- In-memory state ---
const userStates = new Map(); // { step, cart: [{code,name,brand,price,qty}], pendingSelect }
const cache = {
  merged: [],  // [{code,name,brand,qty,price}]
  timestamp: 0
};

// --- Helpers ---
const brandFiles = BRAND_FILES.split(',').map(s => s.trim());
const rawUrl = (fname) => ${GITHUB_RAW_BASE}/${encodeURI(fname)};

async function fetchXlsxRows(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(Fetch failed: ${url} ${res.status});
  const buf = Buffer.from(await res.arrayBuffer());
  const wb = XLSX.read(buf, { type: 'buffer' });
  const sheet = wb.Sheets[wb.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json(sheet);
  return rows;
}

function normalize(str) {
  return String(str || '').trim();
}

async function buildMergedCache(force = false) {
  // Simple TTL: rebuild if older than 120 seconds or force
  const now = Date.now();
  if (!force && cache.timestamp && now - cache.timestamp < 120000 && cache.merged.length) return cache.merged;

  const inventoryRows = await fetchXlsxRows(rawUrl(INVENTORY_FILE));
  // Map brand->priceRows
  const priceMap = {};
  for (const bf of brandFiles) {
    const brand = normalize(bf.replace(/\.xlsx$/i, ''));
    priceMap[brand] = await fetchXlsxRows(rawUrl(bf));
  }

  // Create a map for quick lookup by code for each brand
  const brandCodeIndex = {};
  for (const [brand, rows] of Object.entries(priceMap)) {
    const idx = new Map();
    rows.forEach(r => {
      const code = normalize(r['کد کالا']  r['کد']  r['code']);
      const name = normalize(r['نام کالا'] || r['name']);
      const priceRaw = String(r['قیمت']  r['price']  '').replace(/[^\d]/g, '');
      const price = priceRaw ? Number(priceRaw) : 0;
      if (code) idx.set(code, { code, name, price, brand });
    });
    brandCodeIndex[brand] = idx;
  }

  const merged = [];
  for (const inv of inventoryRows) {
    const code = normalize(inv['کد کالا']  inv['کد']  inv['code']);
    const name = normalize(inv['نام کالا'] || inv['name']);
    const brand = normalize(inv['برند'] || inv['brand']).toLowerCase();
    const qty = Number(inv['تعداد']  inv['qty']  inv['موجودی'] || 0);
    if (!code || !brand) continue;

    const idx = brandCodeIndex[brand];
    let
